# Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import argparse
import socket
import threading

from file_table import FileTable
from concurrent_queue import ConcurrentQueue
from left_error import LeftError
from watch_dog import WatchDog
from left_manager import LeftManager


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, help="peer IP address", required=True)
    args = parser.parse_args()

    print(args.ip)

    file_table = FileTable("share")
    file_event_queue = ConcurrentQueue()
    watchdog = WatchDog(file_table, file_event_queue)

    thread_watch_dog = threading.Thread(name="WatchDog", target=start_watch_dog, args=[watchdog])
    thread_watch_dog.start()

    manager = LeftManager(file_table)
    thread_manager = manager.start_delegate_server()

    try:
        manager.try_client_connect(args.ip)
    except LeftError as e:
        print(f"Illegal peer detected, force disconnect: {e.message}")
    except socket.error as e:
        print(f"Failed to connect to peer {args.ip}: {e}")

    thread_manager.join()


def start_watch_dog(watchdog: WatchDog):
    watchdog.start()


if __name__ == "__main__":
    main()
