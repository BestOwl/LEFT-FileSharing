# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import os
import struct
import socket
import traceback

from file_downloader import FileDownloader
from left_error import LeftError
from logger import Logger
from left_constants import *
from left_packet import LeftPacket, read_packet_from_stream
from stream import SocketStream, FileStream

BUF_SIZE = 20971520  # 1MB


class FileTransferClient:

    def __init__(self, server_address: str, server_port: int, success_callback, fail_callback,
                 client_id):
        self.server_address = server_address
        self.server_port = server_port
        self.success_callback = success_callback
        self.fail_callback = fail_callback
        self.client_id = client_id

        self.logger = Logger(f"FileTransferClient-{client_id}")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.log_verbose(f"Socket connecting to peer {self.server_address}")
        self.sock.connect((self.server_address, self.server_port))
        self.sock_stream = SocketStream(self.sock)

        request = LeftPacket(OPCODE_DOWNLOAD_FILE_CONNECT)
        request.target = struct.pack("!I", self.client_id)
        request.version = b"\x10"
        request.write_bytes(self.sock_stream)

        self.logger.log_info(f"Connected to download service")

    def __del__(self):
        self.sock.close()

    def download(self, file_path):
        success = False
        try:
            request = LeftPacket(OPCODE_DOWNLOAD_FILE)
            request.name = file_path
            request.write_bytes(self.sock_stream)

            response = read_packet_from_stream(self.sock_stream)
            if response.opcode != OPCODE_SUCCESS:
                raise LeftError(f"Download failed with opcode {response.opcode}")

            self.logger.log_info(f"{file_path}: download started")
            # target is a 4-byte header, here we borrow it to store the total file length
            file_total_len = struct.unpack("!I", response.target)[0]

            self.logger.log_verbose(f"{file_path}: opening file handle")
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                self.logger.log_verbose("File dir does not exist, mkdir first")
                os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "wb") as f:
                self.logger.log_verbose("file handle opened, start FileDownloader")
                downloader = FileDownloader(FileStream(f), self.sock_stream, file_total_len, None)
                downloader.download_file()

            self.logger.log_info(f"{file_path}: download completed")
            success = True
        except LeftError as e:
            self.logger.log_error(e.message)
        except socket.error as e:
            traceback.print_exc()
            self.logger.log_error(f"Download failed due to underlying socket failed: {e}")

        if success:
            self.success_callback(file_path)
        else:
            self.fail_callback(file_path)
