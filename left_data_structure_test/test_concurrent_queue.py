# Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import unittest

from left.concurrent_queue import ConcurrentQueue


class MyTestCase(unittest.TestCase):
    def test_fifo(self):
        queue = ConcurrentQueue()
        queue.push(1)
        queue.push(2)
        queue.push(3)

        self.assertEqual(1, queue.pop())
        self.assertEqual(2, queue.pop())
        self.assertEqual(3, queue.pop())

    def test_over_pop(self):
        queue = ConcurrentQueue()
        queue.push(1)
        queue.push(2)
        queue.push(3)

        for _ in range(3):
            queue.pop()

        self.assertIsNone(queue.pop())


if __name__ == '__main__':
    unittest.main()
