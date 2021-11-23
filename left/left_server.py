# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su


from file_table import FileTable, deserialize as deserialize_file_table
from left_packet import *
import file_event


class LeftServer:
    """
    Large Efficient File Transport (LEFT) server
    """

    def __init__(self, client_socket, client_socket_stream: IOStream, peer_address: str, file_table: FileTable,
                 fire_event_callback):
        self.client_socket = client_socket
        self.sock_stream = client_socket_stream
        self.peer_address = peer_address
        self.file_table = file_table
        self.fire_event_callback = fire_event_callback

    def start(self):
        while True:
            packet = read_packet_from_stream(self.sock_stream)
            if packet.opcode == OPCODE_SYNC_FILE_TABLE:
                self.handle_sync_file_table(packet)

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
