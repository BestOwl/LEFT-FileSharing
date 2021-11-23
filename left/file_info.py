# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import stream


def get_normalized_file_path(path: str):
    return path.replace("\\", "/")


class FileInfo:

    def __init__(self, file_path: str, last_modified_time: int, hash_md5: str, is_remote=False):
        self.file_path = get_normalized_file_path(file_path)
        self.last_modified_time = last_modified_time
        self.hash_md5 = hash_md5

        # Represent a file on remote/peer. It will be changed to False after the download is complete
        self.is_remote = is_remote

    def __eq__(self, other):
        if not isinstance(other, FileInfo):
            return False
        else:
            return self.file_path == other.file_path and self.last_modified_time == other.last_modified_time \
                   and self.hash_md5 == other.hash_md5

    def __hash__(self):
        return hash((self.file_path, self.last_modified_time, self.hash_md5))

    def serialize(self):
        buf_stream = stream.new_empty_buffer_stream()
        buf_stream.write_string(self.file_path)
        buf_stream.write_unsigned_long_long(self.last_modified_time)
        buf_stream.write_string(self.hash_md5)
        return buf_stream.buffer


def deserialize_file_info_from_stream(io_stream: stream.IOStream) -> FileInfo:
    file_path, _ = io_stream.read_string()
    last_mtime = io_stream.read_unsigned_long_long()
    hash_md5, _ = io_stream.read_string()
    return FileInfo(file_path, last_mtime, hash_md5)
