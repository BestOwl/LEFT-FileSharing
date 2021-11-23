# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su


from file_table import FileTable, deserialize as deserialize_file_table
from stream import BufferStream
from left_packet import *
import file_event
from logger import Logger


class LeftServer:
    """
    Large Efficient File Transport (LEFT) server
    """

    def __init__(self, client_socket, client_socket_stream: IOStream, peer_address: str, file_table: FileTable,
                 fire_event_callback, peer_down_callback):
        self.client_socket = client_socket
        self.sock_stream = client_socket_stream
        self.peer_address = peer_address
        self.file_table = file_table
        self.fire_event_callback = fire_event_callback
        self.peer_down_callback = peer_down_callback
        self.logger = Logger("LeftServer")
        self._is_dispose = False

    def __del__(self):
        self.dispose()

    def start(self):
        while True:
            if self._is_dispose:
                self.logger.log_warning("server is closing")
                break

            self.logger.log_verbose("read_packet_from_stream call")
            packet = read_packet_from_stream(self.sock_stream)
            self.logger.log_verbose("read_packet_from_stream return")
            if packet is None:
                self.logger.log_warning(f"Peer {self.peer_address} disconnected")
                break
            if packet.opcode == OPCODE_SYNC_FILE_TABLE:
                self.handle_sync_file_table(packet)
            elif packet.opcode == OPCODE_FILE_EVENT:
                self.handle_file_event(packet)
            else:
                self.logger.log_warning(f"Not support opcode {packet.opcode}")
        self.logger.log_warning("server has been stopped")
        self.peer_down_callback(self.peer_address)

    def handle_sync_file_table(self, request: LeftPacket):
        remote_ft = deserialize_file_table(request.data)
        file_events = self.file_table.diff(remote_ft)
        packet = LeftPacket(OPCODE_SUCCESS)
        notify_event_list = file_event.FileEventList()

        for e in file_events:
            if e.event_id == file_event.EVENT_UPDATE_MTIME:
                notify_event_list.append(e)
            elif e.event_id == file_event.EVENT_SEND_NEW_FILE:
                e.event_id = file_event.EVENT_RECEIVE_NEW_FILE
                notify_event_list.append(e)
            elif e.event_id == file_event.EVENT_SEND_MODIFIED_FILE:
                e.event_id = file_event.EVENT_RECEIVE_MODIFIED_FILE
                notify_event_list.append(e)
            else:
                self.fire_event_callback(self.peer_address, e)

        packet.data = notify_event_list.serialize()
        packet.write_bytes(self.sock_stream)

    def handle_file_event(self, request: LeftPacket):
        event = file_event.deserialize_file_event_from_stream(BufferStream(request.data))
        if event.event_id == file_event.EVENT_UPDATE_MTIME:
            pass
            # TODO: update mtime
        else:
            self.logger.log_info(
                f"Received event {event.event_id}: {event.file_info.file_path} from peer {self.peer_address}")
            self.fire_event_callback(self.peer_address, event)

        response = LeftPacket(OPCODE_SUCCESS)
        response.write_bytes(self.sock_stream)

    def dispose(self):
        self._is_dispose = True
