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
from left_server import LeftServer
from left_client import LeftClient
from left_client_manager import LeftClientManager


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, help="peer IP address", required=True)
    args = parser.parse_args()

    print(args.ip)

    file_table = FileTable("../run/share/share")
    file_event_queue = ConcurrentQueue()
    watchdog = WatchDog(file_table, file_event_queue)

    thread_watch_dog = threading.Thread(target=start_watch_dog, args=[watchdog])
    thread_watch_dog.start()

    client_manager = LeftClientManager(file_table)

    server = LeftServer(25560, file_table, client_manager)
    thread_server = threading.Thread(target=start_left_server, args=[server])
    thread_server.start()

    try:
        client_manager.try_connect(args.ip)
    except LeftError as e:
        print(f"Illegal peer detected, force disconnect: {e.message}")
    except socket.error as e:
        print(f"Failed to connect to peer {args.ip}: {e}")

    thread_server.join()


def start_watch_dog(watchdog: WatchDog):
    watchdog.start()


def start_left_server(left_server: LeftServer):
    left_server.start()


if __name__ == "__main__":
    main()
