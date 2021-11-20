# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import os
import time

from file_table import FileTable
from file_helper import scan_path_tree
from concurrent_queue import ConcurrentQueue
import file_helper
from file_event import *


class WatchDog:

    def __init__(self, file_table: FileTable, file_event_queue: ConcurrentQueue):
        self.stop: bool = False
        self.file_table = file_table
        self.file_event_queue = file_event_queue

    def start(self):
        while not self.stop:
            for dir_entry in scan_path_tree(self.file_table.root_path):
                if dir_entry.path not in self.file_table:
                    file_info = self.file_table.add_file_to_file_table_by_dir_entry(dir_entry)
                    self.file_event_queue.push(FileEvent(EVENT_SEND_NEW_FILE, file_info))
                else:
                    self.compare_file_by_mtime_md5(dir_entry)
            time.sleep(0.05)

            delete_list = []
            for path in self.file_table:
                if not os.path.exists(path):
                    delete_list.append(path)
                    self.file_event_queue.push(FileEvent(EVENT_REMOVE_FILE, self.file_table[path]))
            self.file_table.delete_range_from_file_table(delete_list)
            time.sleep(0.05)

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
        if self.file_table[dir_entry.path].last_modified_time != actual_mtime:
            actual_md5 = file_helper.get_file_hash_md5(dir_entry.path)
            if self.file_table[dir_entry.path].hash_md5 != actual_md5:
                self.file_event_queue.push(FileEvent(EVENT_SEND_MODIFIED_FILE, self.file_table[dir_entry.path]))
                self.file_table.update_file_table_md5(dir_entry.path, actual_md5)
            else:
                self.file_table.update_file_table_mtime(dir_entry.path, actual_mtime)
