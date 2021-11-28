# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import stream
from hash_chunk_list import HashChunkList, deserialize_hash_chunk_list_from_stream


def get_normalized_file_path(path: str):
    return path.replace("\\", "/")


class FileInfo:

    def __init__(self, file_path: str, last_modified_time: int, hash_md5_chunks: HashChunkList, is_remote=False):
        self.file_path = get_normalized_file_path(file_path)
        self.last_modified_time = last_modified_time
        self.hash_md5_chunks = hash_md5_chunks  # not None

        # Represent a file on remote/peer. It will be changed to False after the download is complete
        self.is_remote = is_remote

    def __eq__(self, other):
        if not isinstance(other, FileInfo):
            return False
        else:
            return self.file_path == other.file_path and self.last_modified_time == other.last_modified_time \
                   and self.hash_md5_chunks == other.hash_md5_chunks

    def __hash__(self):
        return hash((self.file_path, self.last_modified_time, self.hash_md5_chunks))

    def serialize(self):
        buf_stream = stream.new_empty_buffer_stream()
        buf_stream.write_string(self.file_path)
        buf_stream.write_unsigned_long_long(self.last_modified_time)
        buf_stream.write(self.hash_md5_chunks.serialize())
        return buf_stream.buffer


def deserialize_file_info_from_stream(io_stream: stream.IOStream) -> FileInfo:
    file_path, _ = io_stream.read_string()
    last_mtime = io_stream.read_unsigned_long_long()
    chunks = deserialize_hash_chunk_list_from_stream(io_stream)
    return FileInfo(file_path, last_mtime, chunks)
