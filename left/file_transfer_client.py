# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import os
import struct
import socket

from file_downloader import FileDownloader
from left_error import LeftError
from logger import Logger
from left_constants import *
from left_packet import LeftPacket, read_packet_from_stream
from stream import SocketStream, FileStream
import threading

BUF_SIZE = 20971520  # 1MB


class FileTransferClient:

    def __init__(self, server_address: str, server_port: int, file_path: str, success_callback, fail_callback):
        self.server_address = server_address
        self.server_port = server_port
        self.file_path = file_path
        self.success_callback = success_callback
        self.fail_callback = fail_callback

        self.sock = None
        self.sock_stream = None
        self.thread_download = threading.Thread(name=f"Download-{file_path}", target=self.download)
        self.logger = Logger("FileTransferClient")

    def start(self):
        self.thread_download.start()

    def download(self):
        success = False
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_address, self.server_port))
            self.sock_stream = SocketStream(self.sock)

            self.logger.log_info(f"{self.file_path}: Connected to download service")

            request = LeftPacket(OPCODE_DOWNLOAD_FILE)
            request.name = self.file_path
            request.target = b"LEFT"
            request.version = b"\x10"
            request.write_bytes(self.sock_stream)

            response = read_packet_from_stream(self.sock_stream)
            if response.opcode != OPCODE_SUCCESS:
                raise LeftError(f"Download failed with opcode {response.opcode}")

            self.logger.log_info(f"{self.file_path}: download started")
            # target is a 4-byte header, here we borrow it to store the total file length
            file_total_len = struct.unpack("!I", response.target)[0]

            dir_path = os.path.dirname(self.file_path)
            if not os.path.exists(dir_path):
                self.logger.log_verbose("File dir does not exist, mkdir first")
                os.mkdir(dir_path)
            with open(self.file_path, "wb") as f:
                downloader = FileDownloader(FileStream(f), self.sock_stream, file_total_len, None)
                downloader.download_file()

            self.logger.log_info(f"{self.file_path}: download completed")
            success = True
        except LeftError as e:
            self.logger.log_error(e.message)
        except socket.error as e:
            self.logger.log_error(f"Download failed due to underlying socket failed: {e}")
        finally:
            self.sock.close()

        if success:
            self.success_callback(self.file_path)
        else:
            self.fail_callback(self.file_path)
