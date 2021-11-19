# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

from socket import *
from struct import *

import left.left_packet
from left.left_error import LeftError
from left.left_packet import LeftPacket
from left.left_constants import *
from left.file_table import FileTable


class LeftClient:

    def __init__(self, server_address: str, server_port: int, file_table: FileTable):
        self.socket = None
        self.server_address = server_address
        self.server_port = server_port
        self.file_table = file_table

    def connect(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((self.server_address, self.server_port))
        packet = LeftPacket(OPCODE_CONNECT)
        packet.target = b"LEFT"
        packet.version = b"\x10"
        self.socket.send(packet.to_bytes())

        response = left.left_packet.read_packet_from_socket(self.socket)
        if response.opcode == OPCODE_SUCCESS:
            print(f"Connected to peer server: {self.server_address}:{self.server_port}")
        else:
            raise LeftError(f"Unable to connect to LEFT server: response opcode: {response.opcode}")

        packet = LeftPacket(OPCODE_SYNC_FILE_TABLE)
        temp_file_table = self.file_table.copy_table()
        for path in temp_file_table:
            pack("")

        packet.data = pack("", )

