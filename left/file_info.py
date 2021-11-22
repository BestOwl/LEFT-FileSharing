# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

def get_normalized_file_path(path: str):
    return path.replace("\\", "/")


class FileInfo:

    def __init__(self, file_path: str, last_modified_time: int, hash_md5: str):
        self.file_path = get_normalized_file_path(file_path)
        self.last_modified_time = last_modified_time
        self.hash_md5 = hash_md5

    def __eq__(self, other):
        if not isinstance(other, FileInfo):
            return False
        else:
            return self.file_path == other.file_path and self.last_modified_time == other.last_modified_time \
                   and self.hash_md5 == other.hash_md5

    def __hash__(self):
        return hash((self.file_path, self.last_modified_time, self.hash_md5))
