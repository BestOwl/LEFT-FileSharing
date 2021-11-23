# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import unittest

from left.file_table import FileTable
from left.file_transfer_client import FileTransferClient
from left.file_transfer_server import FileTransferServer

ft = FileTable("share", auto_init_table=False)

def on_download_success():
    pass

def on_download_fail():
    pass

class MyTestCase(unittest.TestCase):
    def test_file_transfer(self):
        FileTransferServer(30001, ft)
        FileTransferClient("127.0.0.1", "share/1.txt")


        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
