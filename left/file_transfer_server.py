# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import math
import socket
import threading
from socket import *
import struct

from file_table import FileTable
from file_provider import FileProvider
from file_pipe import FilePipe
from hash_chunk_list import deserialize_chunk_id_list_from_stream
from left_error import LeftError
from stream import SocketStream, FileStream, IOStream, BufferStream
from left_packet import read_packet_from_stream, LeftPacket
from left_constants import *
from file_helper import get_file_size
from logger import Logger


class FileTransferServer:

    def __init__(self, server_port: int, file_table: FileTable):
        self.server_port = server_port
        self.file_table = file_table

        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind(("", self.server_port))
        self.server_socket.listen(50)
        self.handlers = {}
        self.logger = Logger("FileTransferServer")

    def start(self):
        while True:
            client_socket, address_port = self.server_socket.accept()
            self.logger.log_info(f"{address_port} socket connected")
            client_socket.settimeout(10)
            sock_stream = SocketStream(client_socket)

            try:
                self.logger.log_debug("FileTransferServer handshaking")
                packet = read_packet_from_stream(sock_stream)
                if packet is None or packet.opcode != OPCODE_DOWNLOAD_FILE_CONNECT:
                    raise LeftError("Unknown opcode")

                handler_identifier = struct.unpack("!I", packet.target)[0]
                self.logger.log_debug("FileTransferServer handshake success")
                self.logger.log_info(f"Starting FileTransferHandler for peer {address_port}")
                handler = FileTransferServerHandler(client_socket, sock_stream, address_port, self.file_table,
                                                    handler_identifier=handler_identifier)
                self.handlers[address_port] = handler
            except LeftError as e:
                self.logger.log_error(e.message)
                client_socket.close()
                self.logger.log_error(f"Handshake failed with peer {address_port}, force disconnect")
            except socket.error as e:
                self.logger.log_error(e)
                client_socket.close()
                self.logger.log_error(f"Handshake failed with peer {address_port}, force disconnect")


BUF_SIZE = 20971520  # 10MB


class FileTransferServerHandler:

    def __init__(self, client_socket: socket, sock_stream: IOStream, address_port: (str, int), file_table: FileTable,
                 handler_identifier: int):
        self.sock = client_socket
        self.sock_stream = sock_stream
        self.address_port = address_port
        self.file_table = file_table
        self.handler_identifier = handler_identifier

        self.thread_handler = threading.Thread(name=f"FileTransferServerHandler-{address_port}-{handler_identifier}",
                                               target=self.start)
        self.logger = Logger(self.thread_handler.name)
        self.pipe = FilePipe(self.thread_handler.name)

        self.logger.log_debug(f"Thread {self.thread_handler.name} start")
        self.thread_handler.start()

    def _parse_download_request(self):
        packet = read_packet_from_stream(self.sock_stream)

        if packet is None or packet.opcode == OPCODE_DOWNLOAD_FILE_BYE:
            return None
        elif packet.opcode != OPCODE_DOWNLOAD_FILE and packet.opcode != OPCODE_DOWNLOAD_PARTIAL_FILE \
                or packet.name is None or len(packet.name) == 0:
            raise LeftError("Bad request")

        file_path = packet.name
        download_chunks = None
        if packet.opcode == OPCODE_DOWNLOAD_PARTIAL_FILE:
            buf_stream = BufferStream(packet.data)
            download_chunks = deserialize_chunk_id_list_from_stream(buf_stream)
        return file_path, download_chunks

    def start(self):
        try:
            self.logger.log_verbose("Reading file request")
            parse_result = self._parse_download_request()
            if parse_result is None:
                raise LeftError("Bad request, un-supported opcode")
            file_path, download_chunks = parse_result

            while True:
                if file_path not in self.file_table:
                    response = LeftPacket(OPCODE_NOT_FOUND)
                    response.write_bytes(self.sock_stream)
                    self.logger.log_error(f"File not found {file_path}")
                    return

                self.logger.log_verbose(f"File request receive for: {file_path}")
                total_file_size = get_file_size(file_path)

                response = LeftPacket(OPCODE_SUCCESS)
                # target is a 4-byte header, here we borrow it to store the total file length (unsigned integer)
                response.target = struct.pack("!I", total_file_size)
                response.write_bytes(self.sock_stream)
                self.logger.log_verbose(f"File length {total_file_size} sent")
                with open(file_path, "rb") as fd:
                    self.logger.log_verbose("File handle open, start file transmission")
                    if download_chunks is None:
                        # provider = FileProvider(FileStream(fd), self.sock_stream)
                        # provider.provide_file()
                        self.pipe.pump_file(FileStream(fd), self.sock_stream, total_file_size)
                    else:
                        last_chunk_id = math.ceil(total_file_size / HASH_CHUNK_SIZE) - 1
                        f_stream = FileStream(fd)
                        for chunk_id in download_chunks:
                            fd.seek(chunk_id * HASH_CHUNK_SIZE)

                            size = HASH_CHUNK_SIZE
                            if chunk_id == last_chunk_id:
                                size = total_file_size - chunk_id * HASH_CHUNK_SIZE
                            self.logger.log_debug(f"Send chunk size: {size}")
                            self.pipe.pump_file(f_stream, self.sock_stream, size)

                self.logger.log_info(f"File transmission {file_path} completed")

                self.logger.log_verbose("Continue, reading file request")

                parse_result = self._parse_download_request()
                if parse_result is None:
                    return
                file_path, download_chunks = parse_result
        except LeftError as e:
            self.logger.log_error(f"Illegal file transfer {self.address_port}: {e.message}")
        finally:
            self.logger.log_verbose(f"Thread {self.thread_handler.name} exit")
            self.sock.close()
            self.pipe.dispose()
