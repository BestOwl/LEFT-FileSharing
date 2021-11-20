# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

from socket import *
import threading

import left_packet
from file_table import FileTable, deserialize as deserialize_file_table
from left_client_manager import LeftClientManager
from left_error import LeftError
from left_constants import *


class LeftServer:
    """
    Large Efficient File Transport (LEFT) server
    """

    def __init__(self, port: int, file_table: FileTable, left_client_manager: LeftClientManager):
        self.server_socket = None
        self.server_port = port
        self.file_table = file_table
        self.left_client_manager = left_client_manager

    def start(self):
        self.server_socket: socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(("", self.server_port))
        self.server_socket.listen(2)
        print(f"LEFT server started on port {self.server_port}")

        while True:
            client_socket, address = self.server_socket.accept()
            client_handler = LeftServerClientHandler(client_socket, address, self.file_table, self.left_client_manager)
            client_handler.start()


class LeftServerClientHandler:

    def __init__(self, client_socket, address_port: (str, int), file_table: FileTable,
                 left_client_manager: LeftClientManager):
        self.client_socket = client_socket
        self.address_port = address_port
        self.handler_thread = threading.Thread(target=self.client_socket_handler)
        self.file_table = file_table
        self.left_client_manager = left_client_manager

    def start(self):
        self.handler_thread.start()

    def client_socket_handler(self):
        print(f"Client {self.address_port}: socket connected")
        self.client_socket.settimeout(10)  # 10 seconds timeout for connect request
        try:
            packet = left_packet.read_packet_from_socket(self.client_socket)

            if packet.opcode != OPCODE_CONNECT or packet.target is None or packet.target != b"LEFT":
                raise LeftError("Protocol error: first packet must be a CONNECT packet")

            self.client_socket.send(left_packet.LeftPacket(OPCODE_SUCCESS).to_bytes())

            if not self.left_client_manager.is_connected(self.address_port[0]):
                self.left_client_manager.try_connect(self.address_port[0])

            print(f"Service Level Connection established with peer {self.address_port}")

            self.client_socket.settimeout(None)  # TODO: safe?
            while True:
                packet = left_packet.read_packet_from_socket(self.client_socket)
                if packet.opcode == OPCODE_SYNC_FILE_TABLE:
                    self.handle_sync_file_table(packet)

        except LeftError as e:
            print(f"Client {self.address_port}: {e.message}")
            self.client_socket.close()
            print(f"Client {self.address_port}: force disconnected")

    def handle_sync_file_table(self, request: left_packet.LeftPacket):
        print()
        # remote_ft = deserialize_file_table(request.data)
        # file_events = self.file_table.diff(remote_ft)


