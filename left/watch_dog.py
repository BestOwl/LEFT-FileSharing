# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import os
import time

from file_table import FileTable


# TODO: use faster os.scandir
class WatchDog:

    def __init__(self, file_table: FileTable):
        self.stop: bool = False
        self.file_table = file_table

    def start(self):
        while not self.stop:
            for root, dirs, files in os.walk(self.file_table.root_path):
                for f in files:
                    f_path = os.path.join(root, f)
                    if f_path not in self.file_table.file_table:
                        print(f"+ {f_path}")
                        self.file_table.add_file_to_file_table(f_path)
                    else:
                        self.file_table.compare_file_by_mtime_md5(f_path)
            time.sleep(0.05)

            delete_list = []
            for path in self.file_table.file_table:
                if os.path.exists(path):
                    self.file_table.compare_file_by_mtime_md5(path)
                else:
                    print(f"- {path}")
                    delete_list.append(path)
            self.file_table.delete_range_from_file_table(delete_list)
            time.sleep(0.05)
