# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import os
import hashlib

BUF_SIZE: int = 65536  # 64kb buffer


def get_file_last_modified_time(dir_entry: os.DirEntry) -> int:
    """
    :param dir_entry: os.DirEntry object of a file
    :return: Last modified time of a specific file, in nano seconds
    If the file is currently unreadable in this moment, return None
    """
    return dir_entry.stat().st_mtime_ns


def get_file_hash_md5(path: str):
    """
    :param path: File path string
    :return: MD5 hash of a specific file
    """

    md5 = hashlib.md5()

    if os.access(path, mode=os.R_OK):
        with open(path, mode="rb") as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                md5.update(data)

        return md5.hexdigest()
    else:
        return


def get_file_size(path: str):
    return os.path.getsize(path)


def scan_path_tree(path: str):
    """
    Recursively yield DirEntry objects for given path
    """
    for dir_entry in os.scandir(path):
        if dir_entry.is_dir(follow_symlinks=False):
            yield from scan_path_tree(dir_entry.path)
        else:
            yield dir_entry
