# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import socket
import threading

from logger import Logger
from file_table import FileTable
from file_event import FileEvent
from left_constants import OPCODE_CONNECT, OPCODE_SUCCESS
from stream import SocketStream
from left_error import LeftError
from left_server import LeftServer
from left_client import LeftClient
from left_packet import LeftPacket, read_packet_from_stream


class LeftManager:

    def __init__(self, file_table: FileTable, left_server_port: int, file_server_port: int):
        self.file_table = file_table
        self.left_server_port = left_server_port
        self.file_server_port = file_server_port

        # Client state dictionary
        # Key: server_address
        # Value: ClientManagementInfo object
        self.clients = {}

        # Server state dictionary
        # Key: client_address_port tuple (str, int)
        # Value: ServerManagementInfo object
        self.server_handlers = {}

        self.client_lock = threading.Lock()
        self.server_handler_lock = threading.Lock()

        self.server_socket = None
        self.thread_delegate_server = None

        self.logger = Logger("LeftManager")

    def start_delegate_server(self) -> threading.Thread:
        self.server_socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("", self.left_server_port))
        self.server_socket.listen(10)
        self.logger.log_info(f"LEFT server started on port {self.left_server_port}")

        self.thread_delegate_server = threading.Thread(name="DelegateServer", target=self.delegate_server_accept_loop)
        self.thread_delegate_server.start()
        return self.thread_delegate_server

    def delegate_server_accept_loop(self):
        while True:
            client_socket, address_port = self.server_socket.accept()
            client_socket_stream = SocketStream(client_socket)
            self.logger.log_info(f"Peer client {address_port} socket connected")

            if address_port[0] in self.server_handlers:
                self.logger.log_info(f"Peer {address_port[0]} already connected with this server, reject another CONNECT attempt")
                client_socket.close()
                continue
            smi = ServerManagementInterface(address_port[0])
            self.logger.log_verbose("server_handler_lock lock")
            with self.server_handler_lock:
                self.server_handlers[address_port[0]] = smi
            self.logger.log_verbose("server_handler_lock unlock")

            # TODO: thread pool to handle LEFT handshake
            try:
                # LEFT handshake
                self.logger.log_verbose("handshaking")
                client_socket.settimeout(5)

                packet = read_packet_from_stream(client_socket_stream)
                if packet.opcode != OPCODE_CONNECT or packet.target is None or packet.target != b"LEFT":
                    raise LeftError("Protocol error: first packet must be a CONNECT packet")
                packet = LeftPacket(OPCODE_SUCCESS)
                packet.write_bytes(client_socket_stream)

                self.logger.log_verbose("handshake success")
                client_socket.settimeout(None)  # TODO: safe?
                smi.handshaking.set()
                smi.start(LeftServer(client_socket, client_socket_stream, address_port[0], self.file_table,
                                     self.fire_client_event))
                self.logger.log_verbose("smi set")

                self.logger.log_verbose("is_self_client_connected_to_peer call")
                if not self.is_self_client_connected_to_peer(address_port[0]):
                    self.try_client_connect(address_port[0])
                self.logger.log_verbose("is_self_client_connected_to_peer return")

                self.logger.log_info(f"Service Level Connection established with peer {address_port}")

            except LeftError as e:
                self.logger.log_error(f"Client {address_port}: {e.message}")
                client_socket.close()
                self.logger.log_verbose("server_handler_lock lock")
                with self.server_handler_lock:
                    del self.server_handlers[address_port[0]]
                self.logger.log_verbose("server_handler_lock unlock")
                self.logger.log_verbose("smi set")
                smi.handshaking.set()
                self.logger.log_error(f"Client {address_port}: force disconnected")

    def try_client_connect(self, peer_address: str):
        """
        Try to connect to peer's LeftServer
        :raise LeftError if unable to connect to peer
        """
        client = LeftClient(peer_address, self.left_server_port, self.file_server_port, self.file_table,
                            self.is_self_server_accepted_peer)
        cmi = ClientManagementInterface(peer_address, client)

        self.logger.log_verbose("client_lock lock")
        with self.client_lock:
            self.clients[peer_address] = cmi
        self.logger.log_verbose("client_lock unlock")

        try:
            self.logger.log_verbose("client connect call")
            client.connect()
            self.logger.log_verbose("client connect return")
            cmi.connecting.set()
            self.logger.log_verbose("clear event holding list")
            for e in cmi.event_holding_list:
                cmi.client.event_queue.push(e)
            cmi.event_holding_list = None
        except socket.error:
            client.dispose()
            self.logger.log_verbose("client_lock lock")
            with self.client_lock:
                del self.clients[peer_address]
            self.logger.log_verbose("client_lock unlock")
            cmi.connecting.set()  # set() must be called AFTER del self.clients[address]
            raise

    def is_self_client_connected_to_peer(self, peer_address: str):
        cmi = None
        self.logger.log_verbose("client_lock lock")
        with self.client_lock:
            if peer_address in self.clients:
                cmi = self.clients[peer_address]
        self.logger.log_verbose("client_lock unlock")

        if cmi is not None:
            self.logger.log_verbose("waiting previous connect attempt")
            cmi.connecting.wait()
            self.logger.log_verbose("finish previous connect attempt")
            self.logger.log_verbose("client_lock lock")
            with self.client_lock:
                self.logger.log_verbose("client_lock unlock")
                return cmi.address in self.clients
        else:
            return False

    def is_self_server_accepted_peer(self, peer_address: str):
        smi = None
        self.logger.log_verbose("server_handler_lock lock")
        with self.server_handler_lock:
            if peer_address in self.server_handlers:
                smi = self.server_handlers[peer_address]
        self.logger.log_verbose("server_handler_lock unlock")

        if smi is not None:
            self.logger.log_verbose("waiting previous server handshake")
            smi.handshaking.wait()
            self.logger.log_verbose("previous server handshake complete")
            self.logger.log_verbose("server_handler_lock lock")
            with self.server_handler_lock:
                self.logger.log_verbose("server_handler_lock unlock")
                return smi.address in self.server_handlers
        else:
            return False

    def fire_client_event(self, address: str, event: FileEvent):
        self.logger.log_verbose(f"Event arrive: {event}")
        if self.clients[address].connecting.is_set():
            self.logger.log_verbose(f"Push event to client's event queue")
            self.clients[address].client.fire_event(event)
        else:
            self.logger.log_verbose(f"Client on hold, push event to holding list")
            self.clients[address].event_holding_list.append(event)

    def broadcast_event(self, event: FileEvent):
        for address in self.clients:
            self.fire_client_event(address, event)


class ClientManagementInterface:

    def __init__(self, address: str, client: LeftClient):
        self.address = address
        self.client = client
        self.connecting = threading.Event()
        self.event_holding_list = []


class ServerManagementInterface:

    def __init__(self, address: str):
        self.address = address

        self.handshaking = threading.Event()
        self.server = None
        self.server_thread = None

    def start(self, server: LeftServer):
        self.server = server
        self.server_thread = threading.Thread(target=self._server_thread_start, name=f"LeftServer-{self.address}")
        self.server_thread.start()

    def _server_thread_start(self):
        self.server.start()
