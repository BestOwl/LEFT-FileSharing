# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

from struct import *
import threading
import os

from file_event import *
import file_helper
from hash_chunk_list import deserialize_hash_chunk_list_from_stream
from stream import BufferStream, new_empty_buffer_stream


class FileTable:

    def __init__(self, root_path: str, auto_init_table: bool = True):
        self.root_path = root_path

        # FileInfo dictionary
        # Key: normalized file path
        # Value: FileInfo object
        self.file_dict: dict = {}

        self.lock = threading.Lock()

        if auto_init_table:
            for dir_entry in file_helper.scan_path_tree(root_path):
                self.add_file_to_file_table_by_dir_entry(dir_entry)

    def __contains__(self, item):
        return item in self.file_dict

    def __getitem__(self, item):
        return self.file_dict[item]

    def __iter__(self):
        return self.file_dict.__iter__()

    def __delitem__(self, key):
        del self.file_dict[key]

    def __copy__(self):
        new_ft = FileTable(self.root_path, auto_init_table=False)
        for path in self:
            new_ft.add_file_to_file_table(
                FileInfo(path, self.file_dict[path].last_modified_time, self.file_dict[path].hash_md5_chunks))
        return new_ft

    def add_file_to_file_table_by_dir_entry(self, dir_entry: os.DirEntry) -> FileInfo:
        hash_chunks = file_helper.get_file_hash_md5(dir_entry.path)
        new_file_info = FileInfo(dir_entry.path,
                                 file_helper.get_file_last_modified_time(dir_entry),
                                 hash_chunks)
        return self.add_file_to_file_table(new_file_info)

    def add_file_to_file_table(self, file_info: FileInfo) -> FileInfo:
        self.lock.acquire()
        self.file_dict[file_info.file_path] = file_info
        self.lock.release()
        return file_info

    def delete_from_file_table(self, file_path):
        with self.lock:
            del self.file_dict[file_path]

    def delete_range_from_file_table(self, delete_list: []):
        self.lock.acquire()
        for path in delete_list:
            del self.file_dict[path]
        self.lock.release()

    def update_file_table_md5(self, file_path: str, hash_chunks):
        self.lock.acquire()
        self.file_dict[file_path].hash_md5_chunks = hash_chunks
        self.lock.release()

    def update_file_table_mtime(self, file_path: str, last_modified_time: float):
        self.lock.acquire()
        self.file_dict[file_path].last_modified_time = last_modified_time
        self.lock.release()

    def serialize(self) -> bytes:
        buf_stream = new_empty_buffer_stream()
        for path in self.file_dict:
            buf_stream.write_string(path)
            buf_stream.write_unsigned_long_long(self.file_dict[path].last_modified_time)
            buf_stream.write(self.file_dict[path].hash_md5_chunks.serialize())
        return buf_stream.buffer

    def diff(self, other_file_table) -> []:
        events = []

        def diff_file(file_path: str):
            this_mtime = self[file_path].last_modified_time
            other_mtime = other_file_table[file_path].last_modified_time
            if this_mtime != other_mtime:
                if self[file_path].hash_md5_chunks == other_file_table[file_path].hash_md5_chunks:
                    if this_mtime < other_mtime:
                        events.append(FileEvent(EVENT_UPDATE_MTIME, other_file_table[file_path]))
                    else:
                        events.append(FileEvent(EVENT_UPDATE_MTIME, self[file_path]))
                else:
                    if this_mtime < other_mtime:
                        events.append(FileEvent(EVENT_RECEIVE_MODIFIED_FILE, other_file_table[file_path]))
                    else:
                        events.append(FileEvent(EVENT_SEND_MODIFIED_FILE, self[file_path]))

        for path in self.file_dict:
            if path in other_file_table:
                diff_file(path)
                del other_file_table[path]
            else:
                events.append(FileEvent(EVENT_SEND_NEW_FILE, self[path]))

        for path in other_file_table:
            if path in self:
                diff_file(path)
            else:
                events.append(FileEvent(EVENT_RECEIVE_NEW_FILE, other_file_table[path]))

        return events


class FileTableDeserializeError(Exception):
    def __init__(self, message: str):
        self.message = message


def deserialize(buffer: bytes) -> FileTable:
    remote_ft = FileTable("share", auto_init_table=False)
    buf_stream = BufferStream(buffer)

    while True:
        file_path, _ = buf_stream.read_string()
        if file_path is None:
            break
        mtime = unpack("!Q", buf_stream.read(8))[0]  # size of long long
        chunks = deserialize_hash_chunk_list_from_stream(buf_stream)
        remote_ft.add_file_to_file_table(FileInfo(file_path, mtime, chunks))

    return remote_ft
