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


def scan_path_tree(path: str, ignore_hidden_file_or_folder=True):
    """
    Recursively yield DirEntry objects for given path
    """
    # TODO: skip hidden file and folder
    for dir_entry in os.scandir(path):
        if dir_entry.is_dir(follow_symlinks=False):
            if ignore_hidden_file_or_folder:
                if is_hidden_file(dir_entry.path): # because dir_entry.path for folder does not contains the ending "/"
                    continue
            yield from scan_path_tree(dir_entry.path)
        else:
            if ignore_hidden_file_or_folder:
                if is_hidden_file(dir_entry.path):
                    continue
            yield dir_entry


def is_hidden_file(path) -> bool:
    """
    Whether this file is a hidden file on UNIX-like system.
    This function checks whether the file name is starts with dot ".", if so, will return True.
    This method does not support hidden file on Windows
    :param path: file path
    """
    return os.path.basename(path).startswith(".")


def is_hidden_folder(path) -> bool:
    """
    Similar to is_hidden_file(), but for hidden folder
    The given path must be ended with /
    :param path: folder path ended with /
    """
    assert path[-1] == "/"
    return os.path.split(os.path.split(path)[0])[-1].startswith(".")
