# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

from socket import *

import left_packet
from left_error import LeftError
from left_packet import LeftPacket
from left_constants import *
from file_table import FileTable


class LeftClient:

    def __init__(self, server_address: str, server_port: int, file_table: FileTable):
        self.sock = None
        self.server_address = server_address
        self.server_port = server_port
        self.file_table = file_table
        self.sock_connected = False
        self.is_disposed = False

    def __del__(self):
        self.dispose()

    def connect(self):
        assert not self.is_disposed

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(10)
        self.sock.connect((self.server_address, self.server_port))
        self.sock_connected = True

        packet = LeftPacket(OPCODE_CONNECT)
        packet.target = b"LEFT"
        packet.version = b"\x10"
        self.sock.send(packet.to_bytes())

        response = left_packet.read_packet_from_socket(self.sock)
        if response.opcode == OPCODE_SUCCESS:
            print(f"Connected to peer server: {self.server_address}:{self.server_port}")
        else:
            raise LeftError(f"Unable to connect to LEFT server: response opcode: {response.opcode}")

        packet = LeftPacket(OPCODE_SYNC_FILE_TABLE)
        temp_file_table = self.file_table.__copy__()
        packet.data = temp_file_table.serialize()
        self.sock.send(packet.to_bytes())

    def dispose(self):
        if self.sock is not None:
            if self.sock_connected:
                self.sock.shutdown(SHUT_RDWR)
            self.sock.close()
        self.is_disposed = True
