# Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import argparse
import socket
import threading

from file_table import FileTable
from file_transfer_server import FileTransferServer
from debug_tool import debug_print
from file_event import FileEvent
from left_error import LeftError
from watch_dog import WatchDog
from left_manager import LeftManager


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, help="peer IP address", required=True)
    args = parser.parse_args()

    print(args.ip)

    file_table = FileTable("share")
    manager = LeftManager(file_table, left_server_port=25560, file_server_port=25561)
    watchdog = WatchDog(file_table, event_callback=manager.broadcast_event)

    thread_watch_dog = threading.Thread(name="WatchDog", target=start_watch_dog, args=[watchdog])
    thread_watch_dog.start()

    file_transfer_server = FileTransferServer(25561, file_table)
    thread_file_transfer_server = threading.Thread(name="FileTransferListenServer",
                                                   target=start_file_transfer_server,
                                                   args=[file_transfer_server])
    thread_file_transfer_server.start()
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


def start_file_transfer_server(file_transfer_server: FileTransferServer):
    file_transfer_server.start()


if __name__ == "__main__":
    main()
