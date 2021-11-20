# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import socket
import unittest

from left.file_table import FileTable
from left.left_client import LeftClient


class MyTestCase(unittest.TestCase):

    def test_reconnect(self):
        ft = FileTable("share", auto_init_table=False)
        client = LeftClient("127.0.0.1", 30000, ft)  # must be a unreachable endpoint

        try:
            client.connect()
        except socket.error:
            pass

        client = LeftClient("127.0.0.1", 30000, ft)

        def connect():
            client.connect()

        self.assertRaises(socket.error, connect)


if __name__ == '__main__':
    unittest.main()
