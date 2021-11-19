# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import os
import time

from file_table import FileTable
from file_helper import scan_path_tree


# TODO: use faster os.scandir
class WatchDog:

    def __init__(self, file_table: FileTable):
        self.stop: bool = False
        self.file_table = file_table

    def start(self):
        while not self.stop:
            for dir_entry in scan_path_tree(self.file_table.root_path):
                if dir_entry.path not in self.file_table:
                    print(f"+ {dir_entry.path}")
                    self.file_table.add_file_to_file_table_by_dir_entry(dir_entry)
                else:
                    self.file_table.compare_file_by_mtime_md5(dir_entry)
            time.sleep(0.05)

            delete_list = []
            for path in self.file_table:
                if not os.path.exists(path):
                    print(f"- {path}")
                    delete_list.append(path)
            self.file_table.delete_range_from_file_table(delete_list)
            time.sleep(0.05)


