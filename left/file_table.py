# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

from struct import *
import file_helper
import threading
import os

from file_info import FileInfo
from left.file_event import *


class FileTable:

    def __init__(self, root_path: str, auto_init_table: bool = True):
        self.root_path = root_path
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

    def compare_file_by_mtime_md5(self, dir_entry: os.DirEntry):
        """
        Check whether a specific file has been modified or not
            1.  check the last modification time.
            2.  If it is equal to the modification time stored in the file table, return immediately.
            3.  If not, then check md5 hash.
            4.  If the actual md5 is equal to the md5 stored in the file table, update the modification
                time in the file table, then return.
            5.  If not, this file has been modified, emit a file modification event and update the file table.
        :param dir_entry: os.DirEntry object of a file
        :return: None
        """
        actual_mtime = file_helper.get_file_last_modified_time(dir_entry)
        if self.file_dict[dir_entry.path].last_modified_time != actual_mtime:
            actual_md5 = file_helper.get_file_hash_md5(dir_entry.path)
            if self.file_dict[dir_entry.path].hash_md5 != actual_md5:
                print(f"M {dir_entry.path}")
                self.update_file_table_md5(dir_entry.path, actual_md5)
            else:
                self.update_file_table_mtime(dir_entry.path, actual_mtime)

    def add_file_to_file_table_by_dir_entry(self, dir_entry: os.DirEntry):
        self.lock.acquire()
        self.file_dict[dir_entry.path] = FileInfo(dir_entry.path,
                                                  file_helper.get_file_last_modified_time(dir_entry),
                                                  file_helper.get_file_hash_md5(dir_entry.path))
        self.lock.release()

    def add_file_to_file_table(self, file_info: FileInfo):
        self.lock.acquire()
        self.file_dict[file_info.file_path] = file_info
        self.lock.release()

    def delete_range_from_file_table(self, delete_list: []):
        self.lock.acquire()
        for path in delete_list:
            del self.file_dict[path]
        self.lock.release()

    def update_file_table_md5(self, file_path: str, actual_md5: str):
        self.lock.acquire()
        self.file_dict[file_path].hash_md5 = actual_md5
        self.lock.release()

    def update_file_table_mtime(self, file_path: str, last_modified_time: float):
        self.lock.acquire()
        self.file_dict[file_path].last_modified_time = last_modified_time
        self.lock.release()

    def serialize(self) -> bytes:
        buf = bytes()
        for path in self.file_dict:
            b_path = bytes(path, 'utf-8')
            b_mtime = pack("!I", self.file_dict[path].last_modified_time)
            b_hash_md5 = bytes(self.file_dict[path].hash_md5, 'utf-8')

            sz_mtime = calcsize("!I")
            buf = pack(f"{len(buf)}s {len(b_path)}s s {sz_mtime}s {len(b_hash_md5)}s s",
                       buf, b_path, b"\x00", b_mtime, b_hash_md5, b"\x00")
        return buf

    def diff(self, other_file_table) -> []:
        events = []

        def diff_file(file_path: str):
            this_mtime = self[file_path].last_modified_time
            other_mtime = other_file_table[file_path].last_modified_time
            if this_mtime != other_mtime:
                if self[file_path].hash_md5 == other_file_table[file_path].hash_md5:
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
    sz_buffer = len(buffer)
    pos = 0

    while pos < sz_buffer:
        file_path = ""
        start_pos = pos
        while True:
            if buffer[pos] == 0:
                break
            pos += 1
        file_path = str(unpack_from(f"{pos - start_pos}s", buffer, start_pos)[0], "utf-8")
        pos += 1

        mtime = unpack_from("!I", buffer, pos)[0]
        pos += 4

        hash_md5 = ""
        start_pos = pos
        while True:
            if buffer[pos] == 0:
                break
            pos += 1
        hash_md5 = str(unpack_from(f"{pos - start_pos}s", buffer, start_pos)[0], "utf-8")
        pos += 1

        remote_ft.add_file_to_file_table(FileInfo(file_path, mtime, hash_md5))

    return remote_ft
