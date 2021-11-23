# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import threading
from socket import *

from file_transfer_client import FileTransferClient
from stream import SocketStream
from logger import Logger
import left_packet
from concurrent_queue import ConcurrentQueue
from left_error import LeftError
from left_packet import LeftPacket, read_packet_from_stream
from left_constants import *
from file_table import FileTable
from file_event import *
from stream import BufferStream


class LeftClient:

    def __init__(self, server_address: str, server_port: int, file_server_port: int, file_table: FileTable,
                 is_self_server_accepted_peer_callback):
        self.sock = None
        self.server_address = server_address
        self.server_port = server_port
        self.file_server_port = file_server_port
        self.file_table = file_table
        self.sock_connected = False
        self.is_disposed = False
        self.event_queue = ConcurrentQueue()
        self.thread_event_loop = None
        self.sock_stream = None
        self.is_self_server_accepted_peer_callback = is_self_server_accepted_peer_callback
        self.downloaders = {}
        self.logger = Logger(f"LeftClient-{self.server_address}")

    def __del__(self):
        self.dispose()

    def connect(self, initiate_file_table_sync=True):
        assert not self.is_disposed

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(10)
        self.sock.connect((self.server_address, self.server_port))
        self.sock_connected = True
        self.sock_stream = SocketStream(self.sock)

        packet = LeftPacket(OPCODE_CONNECT)
        packet.target = b"LEFT"
        packet.version = b"\x10"
        packet.write_bytes(self.sock_stream)

        response = left_packet.read_packet_from_stream(self.sock_stream)
        if response.opcode == OPCODE_SUCCESS:
            self.logger.log_info(f"Connected to peer server: {self.server_address}:{self.server_port}")
        else:
            raise LeftError(f"Unable to connect to LEFT server: response opcode: {response.opcode}")

        self.logger.log_verbose("is_self_server_accepted_peer_callback call")
        if initiate_file_table_sync and not self.is_self_server_accepted_peer_callback(self.server_address):
            self.logger.log_verbose("is_self_server_accepted_peer_callback return")
            packet = LeftPacket(OPCODE_SYNC_FILE_TABLE)
            temp_file_table = self.file_table.__copy__()
            packet.data = temp_file_table.serialize()
            packet.write_bytes(self.sock_stream)

            # TODO: SYNC TABLE response
            self.logger.log_verbose("Read file table sync result: read_packet_from_stream call")
            packet = left_packet.read_packet_from_stream(self.sock_stream)
            self.logger.log_verbose("Read file table sync result: read_packet_from_stream return")
            if packet.opcode != OPCODE_SUCCESS:
                self.logger.log_info(f"Sync FileTable failed: opcode {packet.opcode}")
            event_list = deserialize_file_event_list_from_stream(BufferStream(packet.data))
            self.event_queue.push_range(event_list)
            self.logger.log_verbose("FileTable is sync")

        self.sock.settimeout(None)
        self.logger.log_verbose("Client EventLoop started")
        self.thread_event_loop = threading.Thread(name=f"LeftClient-{self.server_address}-EventLoop",
                                                  target=self.event_loop)
        self.thread_event_loop.start()

    def fire_event(self, event):
        self.logger.log_debug(f"Firing event: {event}")
        self.event_queue.push(event)

    def event_loop(self):
        while not self.is_disposed:
            event: FileEvent = self.event_queue.pop()
            if event is not None:
                self.logger.log_debug(f"Dequeue event: {event.event_id} {event.file_info.file_path}")
                if event.event_id == EVENT_RECEIVE_NEW_FILE or event.event_id == EVENT_RECEIVE_MODIFIED_FILE:
                    self.download(event.file_info.file_path, self.server_address)
                else:
                    packet = LeftPacket(OPCODE_FILE_EVENT)
                    if event.event_id == EVENT_SEND_NEW_FILE:
                        event.event_id = EVENT_RECEIVE_NEW_FILE
                    elif event.event_id == EVENT_SEND_MODIFIED_FILE:
                        event.event_id = EVENT_RECEIVE_MODIFIED_FILE
                    self.logger.log_info(f"Sending event {event.event_id} to peer {self.server_address}")
                    packet.data = event.serialize()
                    packet.write_bytes(self.sock_stream)

                    response = read_packet_from_stream(self.sock_stream)
                    if response.opcode != OPCODE_SUCCESS:
                        pass
                        # TODO: non-successful file event
            # else:
                # self.logger.log_verbose("EventLoop: No event")
        self.logger.log_warning("Client disposed, event loop stopped")

    def download(self, file_path: str, peer_address: str):
        client = FileTransferClient(peer_address, self.file_server_port, file_path)
        self.downloaders[peer_address] = client
        client.start()
        # TODO: download complete callback

    def dispose(self):
        if self.sock is not None:
            if self.sock_connected:
                self.sock.shutdown(SHUT_RDWR)
            self.sock.close()
        self.is_disposed = True
