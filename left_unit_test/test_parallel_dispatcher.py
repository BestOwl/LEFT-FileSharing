# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import time
import unittest

from left.parallel_dispatcher import ParallelDispatcher


def execute_func():
    time.sleep(5)


class MyTestCase(unittest.TestCase):

    def test_dispatch(self):
        dispatcher = ParallelDispatcher(10)
        for i in range(100):
            dispatcher.execute(execute_func)
        dispatcher.join()
        self.assertEqual(0, dispatcher.threads)


if __name__ == '__main__':
    unittest.main()
