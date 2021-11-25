# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import time
from collections import deque


def main():
    test_round = 1000000

    print("Test ArrayList push pop")
    queue = []
    t_start = time.perf_counter()
    for i in range(test_round):
        queue.append(1)
    for i in range(test_round):
        queue.pop()
    t_end = time.perf_counter()
    print(f"ArrayList push pop done: {t_end - t_start}")

    time.sleep(3)

    queue = deque()
    print("Test collections deque push pop")
    t_start = time.perf_counter()
    for i in range(test_round):
        queue.append(1)
    for i in range(test_round):
        queue.pop()
    t_end = time.perf_counter()
    print(f"collections deque push pop done: {t_end - t_start}")

    time.sleep(3)

    linked_queue = LinkedList()
    t_start = time.perf_counter()
    for i in range(test_round):
        linked_queue.push(1)
    for i in range(test_round):
        linked_queue.pop()
    t_end = time.perf_counter()
    print(f"LinkedList push pop done: {t_end - t_start}")


class LinkedList:
    """
    Home-made linked list
    """
    def __init__(self):
        self.head = None
        self.tail = None

    def push(self, value):
        node = LinkedListNode(value, None, None)

        if self.tail is not None:
            node.prev_node = self.tail
            self.tail.next_node = node
        else:
            self.head = node

        self.tail = node

    def pop(self):
        if self.head is not None:
            value = self.head.value
            self.head = self.head.next_node
            return value


class LinkedListNode:
    def __init__(self, value, prev_node, next_node):
        self.value = value
        self.prev_node = prev_node
        self.next_node = next_node


if __name__ == "__main__":
    main()
