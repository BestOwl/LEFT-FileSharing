# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

from file_info import FileInfo
import file_info
import stream

EVENT_UPDATE_MTIME = b"\xD0"
EVENT_SEND_NEW_FILE = b"\xD1"
EVENT_RECEIVE_NEW_FILE = b"\xD2"
EVENT_SEND_MODIFIED_FILE = b"\xD3"
EVENT_RECEIVE_MODIFIED_FILE = b"\xD4"
EVENT_REMOVE_FILE = b"\xD5"

_event_str_map = {
    EVENT_UPDATE_MTIME: "@UpdateMtime",
    EVENT_SEND_NEW_FILE: "@SendNewFile",
    EVENT_RECEIVE_NEW_FILE: "@ReceiveNewFile",
    EVENT_SEND_MODIFIED_FILE: "@SendModifiedFile",
    EVENT_RECEIVE_MODIFIED_FILE: "@ReceiveModifiedFile",
    EVENT_REMOVE_FILE: "@RemoveFile"
}


class FileEvent:

    def __init__(self, event_id: bytes, file_info: FileInfo):
        self.event_id = event_id
        self.file_info = file_info

    def __eq__(self, other):
        if not isinstance(other, FileEvent):
            return False
        else:
            return self.event_id == other.event_id and self.file_info == other.file_info

    def __hash__(self):
        return hash((self.event_id, self.file_info))

    def __str__(self):
        return f"{_event_str_map[self.event_id]} {self.file_info.file_path} {self.file_info.last_modified_time} " \
               f"chunks:{self.file_info.hash_md5_chunks}"

    def serialize(self):
        buf_stream = stream.new_empty_buffer_stream()
        buf_stream.write(self.event_id)
        buf_stream.write(self.file_info.serialize())
        return buf_stream.buffer


def deserialize_file_event_from_stream(io_stream: stream.IOStream) -> FileEvent:
    event_id = io_stream.read(1)
    f_info = file_info.deserialize_file_info_from_stream(io_stream)
    return FileEvent(event_id, f_info)


class FileEventList:

    def __init__(self):
        self.events = []

    def __getitem__(self, item):
        return self.events[item]

    def __iter__(self):
        return self.events.__iter__()

    def append(self, file_event: FileEvent):
        self.events.append(file_event)

    def serialize(self):
        buf_stream = stream.new_empty_buffer_stream()
        for event in self.events:
            buf_stream.write(event.event_id)
            buf_stream.write(event.file_info.serialize())
        return buf_stream.buffer


def deserialize_file_event_list_from_stream(io_stream: stream.IOStream) -> FileEventList:
    event_list = FileEventList()
    while True:
        event_id = io_stream.read(1)
        if event_id == b"":
            break
        f_info = file_info.deserialize_file_info_from_stream(io_stream)
        event_list.append(FileEvent(event_id, f_info))
    return event_list
