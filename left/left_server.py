# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

from socket import *
import threading

import left_packet
from left_error import LeftError
from file_table import FileTable
from watch_dog import WatchDog
from left_constants import *


class LeftServer:
    """
    Large Efficient File Transport (LEFT) server
    """

    def __init__(self, port: int, file_table: FileTable):
        self.server_socket = None
        self.server_port = port
        self.clients: dict = {}
        self.file_table = file_table
        self.watchdog = WatchDog(self.file_table)

    def start(self):
        thread_watch_dog = threading.Thread(target=self.start_watch_dog)
        thread_watch_dog.start()

        self.server_socket: socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(("", self.server_port))
        self.server_socket.listen(2)
        print(f"LEFT server started on port {self.server_port}")

        while True:
            client_socket, address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.client_socket_handler, args=(client_socket, address))
            self.clients[address] = client_thread
            client_thread.start()

    def start_watch_dog(self):
        self.watchdog.start()

    def client_socket_handler(self, client_socket: socket, address: (str, int)):
        print(f"Client {address}: socket connected")
        client_socket.settimeout(30)  # 30 seconds timeout for connect request
        try:
            packet = left_packet.read_packet_from_socket(client_socket)

            if packet.opcode != OPCODE_CONNECT or packet.target is None or packet.target != b"LEFT":
                raise LeftError("Protocol error: first packet must be a CONNECT packet")

            self.clients[address] = client_socket
            client_socket.send(left_packet.LeftPacket(OPCODE_SUCCESS).to_bytes())

            print(f"Client {address}: peer service level connection established")

            client_socket.settimeout(0)  # TODO: safe?
            while True:
                packet = left_packet.read_packet_from_socket(client_socket)
                if packet.opcode == OPCODE_SYNC_FILE_TABLE:
                    self.handle_sync_file_table(packet)

        except LeftError as e:
            print(f"Client {address}: {e.message}")
            client_socket.close()
            print(f"Client {address}: force disconnected")

    def handle_sync_file_table(self, request: left_packet.LeftPacket):
        print()

