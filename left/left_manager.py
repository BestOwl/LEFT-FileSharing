# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import socket
import threading

from file_table import FileTable
from file_event import FileEvent
from left.debug_tool import debug_print
from left_constants import OPCODE_CONNECT, OPCODE_SUCCESS
from stream import SocketStream
from left_error import LeftError
from left_server import LeftServer
from left_client import LeftClient
from left_packet import LeftPacket, read_packet_from_stream


class LeftManager:

    def __init__(self, file_table: FileTable, left_server_port: int = 25560):
        self.file_table = file_table
        self.left_server_port = left_server_port

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

    def start_delegate_server(self) -> threading.Thread:
        self.server_socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("", self.left_server_port))
        self.server_socket.listen(10)
        print(f"LEFT server started on port {self.left_server_port}")

        self.thread_delegate_server = threading.Thread(target=self.delegate_server_accept_loop)
        self.thread_delegate_server.setName("DelegateServer")
        self.thread_delegate_server.start()
        return self.thread_delegate_server

    def delegate_server_accept_loop(self):
        while True:
            client_socket, address_port = self.server_socket.accept()
            client_socket_stream = SocketStream(client_socket)
            print(f"Peer client {address_port} socket connected")

            if address_port[0] in self.server_handlers:
                print(f"Peer {address_port[0]} already connected with this server, reject another CONNECT attempt")
                client_socket.close()
                continue
            smi = ServerManagementInterface(address_port[0])
            debug_print("server_handler_lock lock")
            with self.server_handler_lock:
                self.server_handlers[address_port[0]] = smi
            debug_print("server_handler_lock unlock")

            # TODO: thread pool to handle LEFT handshake
            try:
                # LEFT handshake
                debug_print("handshaking")
                client_socket.settimeout(5)

                packet = read_packet_from_stream(client_socket_stream)
                if packet.opcode != OPCODE_CONNECT or packet.target is None or packet.target != b"LEFT":
                    raise LeftError("Protocol error: first packet must be a CONNECT packet")
                client_socket_stream.write(LeftPacket(OPCODE_SUCCESS).to_bytes())

                debug_print("handshake success")
                client_socket.settimeout(None)  # TODO: safe?
                smi.handshaking.set()
                smi.start(LeftServer(client_socket, client_socket_stream, address_port[0], self.file_table,
                                     self.fire_client_event))
                debug_print("smi set")

                debug_print("is_self_client_connected_to_peer call")
                if not self.is_self_client_connected_to_peer(address_port[0]):
                    self.try_client_connect(address_port[0])
                debug_print("is_self_client_connected_to_peer return")

                print(f"Service Level Connection established with peer {address_port}")

            except LeftError as e:
                print(f"Client {address_port}: {e.message}")
                client_socket.close()
                debug_print("server_handler_lock lock")
                with self.server_handler_lock:
                    del self.server_handlers[address_port[0]]
                debug_print("server_handler_lock unlock")
                debug_print("smi set")
                smi.handshaking.set()
                print(f"Client {address_port}: force disconnected")

    def try_client_connect(self, peer_address: str):
        """
        Try to connect to peer's LeftServer
        :raise LeftError if unable to connect to peer
        """
        client = LeftClient(peer_address, self.left_server_port, self.file_table, self.is_self_server_accepted_peer)
        cmi = ClientManagementInfo(peer_address, client)

        debug_print("client_lock lock")
        with self.client_lock:
            self.clients[peer_address] = cmi
        debug_print("client_lock unlock")

        try:
            debug_print("client connect call")
            client.connect()
            debug_print("client connect return")
            cmi.connecting.set()
        except socket.error:
            client.dispose()
            debug_print("client_lock lock")
            with self.client_lock:
                del self.clients[peer_address]
            debug_print("client_lock unlock")
            cmi.connecting.set()  # set() must be called AFTER del self.clients[address]
            raise


    def is_self_client_connected_to_peer(self, peer_address: str):
        cmi = None
        debug_print("client_lock lock")
        with self.client_lock:
            if peer_address in self.clients:
                cmi = self.clients[peer_address]
        debug_print("client_lock unlock")

        if cmi is not None:
            debug_print("waiting previous connect attempt")
            cmi.connecting.wait()
            debug_print("finish previous connect attempt")
            debug_print("client_lock lock")
            with self.client_lock:
                debug_print("client_lock unlock")
                return cmi.address in self.clients
        else:
            return False

    def is_self_server_accepted_peer(self, peer_address: str):
        smi = None
        debug_print("server_handler_lock lock")
        with self.server_handler_lock:
            if peer_address in self.server_handlers:
                smi = self.server_handlers[peer_address]
        debug_print("server_handler_lock unlock")

        if smi is not None:
            debug_print("waiting previous server handshake")
            smi.handshaking.wait()
            debug_print("previous server handshake complete")
            debug_print("server_handler_lock lock")
            with self.server_handler_lock:
                debug_print("server_handler_lock unlock")
                return smi.address in self.server_handlers
        else:
            return False

    def fire_client_event(self, address: str, event: FileEvent):
        self.clients[address].client.fire_event(event)


class ClientManagementInfo:

    def __init__(self, address: str, client: LeftClient):
        self.address = address
        self.client = client
        self.connecting = threading.Event()


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
