# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import threading
from socket import *
import struct

from file_table import FileTable
from left_error import LeftError
from stream import SocketStream
from left_packet import read_packet_from_stream, LeftPacket
from left_constants import *
from file_helper import get_file_size
from logger import Logger


class FileTransferServer:

    def __init__(self, server_port: int, file_table: FileTable):
        self.server_port = server_port
        self.file_table = file_table

        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(("", self.server_port))
        self.server_socket.listen(5)
        self.handlers = {}
        self.logger = Logger("FileTransferServer")

    def start(self):
        while True:
            client_socket, address_port = self.server_socket.accept()
            self.logger.log_info(f"Downloader {address_port} socket connected")
            handler = FileTransferServerHandler(client_socket, address_port, self.file_table)
            self.handlers[address_port] = handler


BUF_SIZE = 20971520  # 10MB


class FileTransferServerHandler:

    def __init__(self, client_socket: socket, address_port: (str, int), file_table: FileTable):
        self.sock = client_socket
        self.address_port = address_port
        self.file_table = file_table
        self.sock_stream = SocketStream(client_socket)
        self.thread_handler = threading.Thread(name=f"FileTransferServerHandler-{address_port}", target=self.start)
        self.logger = Logger(self.thread_handler.name)
        self.logger.log_debug(f"Thread {self.thread_handler.name} start")
        self.thread_handler.start()

    def start(self):
        try:
            file_path = self.handshake()

            if file_path not in self.file_table:
                response = LeftPacket(OPCODE_NOT_FOUND)
                response.write_bytes(self.sock_stream)
                self.logger.log_error(f"File not found {file_path}")
                return

            response = LeftPacket(OPCODE_SUCCESS)
            # target is a 4-byte header, here we borrow it to store the total file length (unsigned integer)
            response.target = struct.pack("!I", get_file_size(file_path))
            response.write_bytes(self.sock_stream)

            with open(file_path, "rb") as f:
                while True:
                    buf = f.read(BUF_SIZE)
                    if buf == b"":
                        break
                    else:
                        self.sock.send(buf)

            self.logger.log_info(f"File transmission {file_path} completed")
        except LeftError as e:
            self.logger.log_error(f"Illegal file transfer {self.address_port}: {e.message}")
        self.sock.close()

    def handshake(self) -> str:
        packet = read_packet_from_stream(self.sock_stream)
        if packet.opcode != OPCODE_DOWNLOAD_FILE or packet.target != b"LEFT" or packet.name is None or len(
                packet.name) == 0:
            raise LeftError("handshake error")

        return packet.name
