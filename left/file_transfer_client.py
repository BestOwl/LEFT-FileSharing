# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su
import struct
from socket import *

from debug_tool import debug_print
from left_constants import *
from left_packet import LeftPacket, read_packet_from_stream
from stream import SocketStream
import threading

BUF_SIZE = 20971520  # 1MB


class FileTransferClient:

    def __init__(self, server_address: str, server_port: int, file_path: str):
        self.server_address = server_address
        self.server_port = server_port
        self.file_path = file_path
        self.sock = None
        self.sock_stream = None
        self.thread_download = threading.Thread(name=f"Download-{file_path}", target=self.download)

    def start(self):
        self.thread_download.start()

    def download(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.server_address, self.server_port))
        self.sock_stream = SocketStream(self.sock)

        print(f"Downloader> {self.file_path}: Connected to download service")

        request = LeftPacket(OPCODE_DOWNLOAD_FILE)
        request.name = self.file_path
        request.target = b"LEFT"
        request.version = b"\x10"
        request.write_bytes(self.sock_stream)

        response = read_packet_from_stream(self.sock_stream)
        if response.opcode != OPCODE_SUCCESS:
            print(f"Download failed: opcode {response.opcode}")
            return

        print(f"Downloader> {self.file_path}: download started")
        # target is a 4-byte header, here we borrow it to store the total file length
        file_total_len = struct.unpack("!I", response.target)[0]
        total_receive_sz = 0
        with open(self.file_path, "wb") as f:

            while True:
                buf = bytearray(BUF_SIZE)
                receive_sz = self.sock.recv_into(buf, BUF_SIZE)
                total_receive_sz += receive_sz

                print(f"Downloader> {self.file_path}: {total_receive_sz} / {file_total_len} bytes")

                if 0 < receive_sz <= BUF_SIZE:
                    f.write(buf)
                else:
                    break

        print(f"Downloader> {self.file_path}: download completed")
