# Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import threading


class ConcurrentQueue:
    """
    Thread-safe First In First Out (FIFO) queue
    """

    def __init__(self, blocking_mode=False):
        """
        Initialize a thread-safe FIFO queue
        :param blocking_mode: pop() will block if the queue is empty until new content arrived
        """
        self.list = []
        self.blocking_mode = blocking_mode
        self._blocking = threading.Event()

    def push(self, item):
        self.list.append(item)
        if self._blocking:
            self._blocking.set()

    def push_range(self, items):
        for i in items:
            self.list.append(i)
        self._blocking.set()

    def pop(self):
        if len(self.list) == 0:
            if self.blocking_mode:
                self._blocking.clear()
                self._blocking.wait()
            else:
                return None

        return self.list.pop(0)
