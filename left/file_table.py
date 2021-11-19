# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import left.file_helper
import threading
import os


class FileInfo:

    def __init__(self, path: str, last_modified_time: int, hash_md5: str):
        self.path = path
        self.last_modified_time = last_modified_time
        self.hash_md5 = hash_md5


class FileTable:

    def __init__(self, root_path: str):
        self.root_path = root_path
        self.file_table: dict = {}
        self.lock = threading.Lock()

        for root, dirs, files in os.walk(self.root_path):
            for f in files:
                f_path = os.path.join(root, f)
                self.add_file_to_file_table(f_path)

    def compare_file_by_mtime_md5(self, file_path: str):
        """
        Check whether a specific file has been modified or not
            1.  check the last modification time.
            2.  If it is equal to the modification time stored in the file table, return immediately.
            3.  If not, then check md5 hash.
            4.  If the actual md5 is equal to the md5 stored in the file table, update the modification
                time in the file table, then return.
            5.  If not, this file has been modified, emit a file modification event and update the file table.
        :param file_path: file path string
        :return: None
        """
        actual_mtime = left.file_helper.get_file_last_modified_time(file_path)
        if self.file_table[file_path].last_modified_time != actual_mtime:
            actual_md5 = left.file_helper.get_file_hash_md5(file_path)
            if self.file_table[file_path].hash_md5 != actual_md5:
                print(f"M {file_path}")
                self.update_file_table_md5(file_path, actual_md5)
            else:
                self.update_file_table_mtime(file_path, actual_mtime)

    def add_file_to_file_table(self, file_path: str):
        self.lock.acquire()
        self.file_table[file_path] = FileInfo(file_path,
                                              left.file_helper.get_file_last_modified_time(file_path),
                                              left.file_helper.get_file_hash_md5(file_path))
        self.lock.release()

    def delete_range_from_file_table(self, delete_list: []):
        self.lock.acquire()
        for path in delete_list:
            del self.file_table[path]
        self.lock.release()

    def update_file_table_md5(self, file_path: str, actual_md5: str):
        self.lock.acquire()
        self.file_table[file_path].hash_md5 = actual_md5
        self.lock.release()

    def update_file_table_mtime(self, file_path: str, last_modified_time: float):
        self.lock.acquire()
        self.file_table[file_path].last_modified_time = last_modified_time
        self.lock.release()

    def copy_table(self) -> dict:
        self.lock.acquire()
        copied_file_table = self.file_table.copy()
        self.lock.release()
        return copied_file_table
