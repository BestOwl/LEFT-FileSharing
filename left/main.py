# Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import argparse
import threading
from left.file_table import FileTable
from left.left_server import LeftServer
from left.left_client import LeftClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, help="peer IP address", required=True)
    args = parser.parse_args()

    print(args.ip)

    file_table = FileTable("share")
    server = LeftServer(25560, file_table)
    thread_server = threading.Thread(target=start_left_server, args=[server])
    thread_server.start()

    client = LeftClient(args.ip, 25560, file_table)
    client.connect()


def start_left_server(left_server: LeftServer):
    left_server.start()


if __name__ == "__main__":
    main()
