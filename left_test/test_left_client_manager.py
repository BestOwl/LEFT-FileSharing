# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su
import threading
import time
import unittest

from left.file_table import FileTable
from left.left_client_manager import LeftClientManager
from left.left_server import LeftServer


class MyTestCase(unittest.TestCase):

    #  TODO:
    def test_is_connected(self):
        ft = FileTable("share", auto_init_table=False)
        manager = LeftClientManager(ft, left_server_port=30000)
        left_server = LeftServer(30000, ft, manager)

        def start_server():
            left_server.start()

        thread_server = threading.Thread(target=start_server)
        thread_server.start()

        time.sleep(3)

        def client_connect():
            manager.try_connect("127.0.0.1")

        thread_client = threading.Thread(target=client_connect)
        thread_client.start()
        is_connected = manager.is_connected("127.0.0.1")
        self.assertTrue(is_connected)
        thread_server.join()


if __name__ == '__main__':
    unittest.main()
