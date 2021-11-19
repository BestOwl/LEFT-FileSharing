# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import os
import hashlib

BUF_SIZE: int = 65536  # 64kb buffer


def get_file_last_modified_time(path: str):
    """
    :param path: File path string
    :return: Last modified time of a specific file
    """
    return os.path.getmtime(path)


def get_file_hash_md5(path: str):
    """
    :param path: File path string
    :return: MD5 hash of a specific file
    """

    md5 = hashlib.md5()

    with open(path, mode="rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()
