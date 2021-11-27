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


class DataQueue(ConcurrentQueue):

    def __init__(self, total_data_size_limit=8192):
        super().__init__(blocking_mode=True)
        self.total_data_size_limit = total_data_size_limit
        self._data_size = 0
        self._clear_threshold = 0
        self._sz_blocking = threading.Event()

    def push(self, item: bytes):
        data_sz = len(item)
        if data_sz + self._data_size > self.total_data_size_limit:
            self._clear_threshold = self.total_data_size_limit - self._data_size
            self._sz_blocking.clear()
            self._sz_blocking.wait()
        self._data_size += data_sz
        super().push(item)

    def push_range(self, items):
        for item in items:
            self.push(item)

    def pop(self):
        ret = super().pop()
        self._data_size -= len(ret)
        if self._data_size <= self.total_data_size_limit:
            self._sz_blocking.set()
        return ret
