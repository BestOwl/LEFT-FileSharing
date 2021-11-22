# Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import threading


class ConcurrentQueue:
    """
    Thread-safe First In First Out (FIFO) queue
    """

    def __init__(self):
        self.list = []

    def push(self, item):
        self.list.append(item)

    def pop(self):
        ret = None
        if len(self.list) > 0:
            ret = self.list.pop(0)
        return ret