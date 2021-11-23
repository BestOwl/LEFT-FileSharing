# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import threading
from socket import *

from left.debug_tool import debug_print
from left.file_transfer_client import FileTransferClient
from stream import SocketStream

import left_packet
from concurrent_queue import ConcurrentQueue
from left_error import LeftError
from left_packet import LeftPacket
from left_constants import *
from file_table import FileTable
from file_event import deserialize_file_event_list_from_stream, EVENT_RECEIVE_NEW_FILE, EVENT_RECEIVE_MODIFIED_FILE
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
            print(f"Connected to peer server: {self.server_address}:{self.server_port}")
        else:
            raise LeftError(f"Unable to connect to LEFT server: response opcode: {response.opcode}")

        debug_print("is_self_server_accepted_peer_callback call")
        if initiate_file_table_sync and not self.is_self_server_accepted_peer_callback(self.server_address):
            debug_print("is_self_server_accepted_peer_callback return")
            packet = LeftPacket(OPCODE_SYNC_FILE_TABLE)
            temp_file_table = self.file_table.__copy__()
            packet.data = temp_file_table.serialize()
            packet.write_bytes(self.sock_stream)

            # TODO: SYNC TABLE response
            packet = left_packet.read_packet_from_stream(self.sock_stream)
            if packet.opcode != OPCODE_SUCCESS:
                print(f"Sync FileTable failed: opcode {packet.opcode}")
            event_list = deserialize_file_event_list_from_stream(BufferStream(packet.data))
            self.event_queue.push_range(event_list)

        self.thread_event_loop = threading.Thread(name=f"LeftClient-{self.server_address}-EventLoop",
                                                  target=self.event_loop)
        self.thread_event_loop.start()

    def fire_event(self, event):
        self.event_queue.push(event)

    def event_loop(self):
        while not self.is_disposed:
            event = self.event_queue.pop()
            if event is not None:
                debug_print(f"Dequeue event: {event}")
                if event.event_id == EVENT_RECEIVE_NEW_FILE or event.event_id == EVENT_RECEIVE_MODIFIED_FILE:
                    self.download(event.file_info.file_path, self.server_address)
                else:
                    packet = LeftPacket()
                    self.sock_stream

    def download(self, file_path: str, peer_address: str):
        client = FileTransferClient(peer_address, self.file_server_port, file_path)
        self.downloaders[peer_address] = client
        client.start()
        #TODO: download complete callback

    def dispose(self):
        if self.sock is not None:
            if self.sock_connected:
                self.sock.shutdown(SHUT_RDWR)
            self.sock.close()
        self.is_disposed = True
