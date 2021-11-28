# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import os
import time

from file_table import FileTable
from file_helper import scan_path_tree
import file_helper
from file_event import *
from file_info import get_normalized_file_path
from logger import Logger


class WatchDog:

    def __init__(self, file_table: FileTable, event_callback):
        self.stop: bool = False
        self.file_table = file_table
        self.event_callback = event_callback
        self.logger = Logger("WatchDog")

    def dispatch_event(self, event: FileEvent, reason: str):
        self.logger.log_debug(f"Dispatch watchdog event: {event}. Reason: {reason}")
        self.event_callback(event)

    def start(self):
        while not self.stop:
            for dir_entry in scan_path_tree(self.file_table.root_path, ignore_hidden_file_or_folder=True):
                path = get_normalized_file_path(dir_entry.path)

                # skip
                if not os.access(path, mode=os.R_OK):
                    continue

                if path not in self.file_table:
                    file_info = self.file_table.add_file_to_file_table_by_dir_entry(dir_entry)
                    self.dispatch_event(FileEvent(EVENT_SEND_NEW_FILE, file_info), "File not in table")
                else:
                    if not self.file_table[path].is_remote:
                        actual_mtime = file_helper.get_file_last_modified_time(dir_entry)
                        self._compare_file_by_mtime_md5(path, actual_mtime)
            time.sleep(0.05)

            delete_list = []
            for path in self.file_table:
                if not self.file_table[path].is_remote and not os.path.exists(path):
                    delete_list.append(path)
                    self.dispatch_event(FileEvent(EVENT_REMOVE_FILE, self.file_table[path]), "File has been removed")
            self.file_table.delete_range_from_file_table(delete_list)
            time.sleep(0.05)

    def _compare_file_by_mtime_md5(self, path: str, actual_mtime: int):
        """
        Check whether a specific file has been modified or not
            1.  check the last modification time.
            2.  If it is equal to the modification time stored in the file table, return immediately.
            3.  If not, then check md5 hash.
            4.  If the actual md5 is equal to the md5 stored in the file table, update the modification
                time in the file table, then return.
            5.  If not, this file has been modified, emit a file modification event and update the file table.
        :return: None
        """
        if self.file_table[path].last_modified_time != actual_mtime:
            hash_chunks = file_helper.get_file_hash_md5(path)

            # the file we want to check might be temporarily unreadable due to in-progress file copy operation or other
            # operation, so the actual_md5 might be None if this is the case
            if len(hash_chunks) > 0:
                if self.file_table[path].hash_md5_chunks != hash_chunks:
                    recorded_chunks = self.file_table[path].hash_md5_chunks
                    if len(recorded_chunks) > 0:
                        self.dispatch_event(FileEvent(EVENT_SEND_MODIFIED_FILE, self.file_table[path]),
                                            "Actual MD5 do not match")
                    self.file_table.update_file_table_md5(path, hash_chunks)
                else:
                    self.file_table.update_file_table_mtime(path, actual_mtime)
