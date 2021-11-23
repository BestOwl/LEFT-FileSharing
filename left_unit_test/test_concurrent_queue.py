# Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import threading
import time
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

    def test_event_loop(self):
        event_queue = ConcurrentQueue()

        def dummy_event_source(q: ConcurrentQueue):
            for i in range(10):
                time.sleep(1)
                q.push(i)

        def event_loop(q: ConcurrentQueue):
            while True:
                event = q.pop()
                if event is not None:
                    print(f"Event arrived {event}")
                    if event == 9:
                        break

        thread_event_source = threading.Thread(target=dummy_event_source, args=[event_queue])
        thread_event_loop = threading.Thread(target=event_loop, args=[event_queue])

        thread_event_source.start()
        thread_event_loop.start()

        thread_event_loop.join()
        thread_event_source.join()


if __name__ == '__main__':
    unittest.main()
