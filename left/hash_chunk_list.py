# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

from stream import new_empty_buffer_stream, IOStream


class ChunkIdList:

    def __init__(self, chunk_id_list=None):
        """
        :param chunk_id_list: int list
        """
        if chunk_id_list is not None:
            self.chunk_id_list = chunk_id_list
        else:
            self.chunk_id_list = []

    def __str__(self):
        return str(self.chunk_id_list)

    def __len__(self):
        return len(self.chunk_id_list)

    def __getitem__(self, item):
        return self.chunk_id_list[item]

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ChunkIdList):
            return False
        if len(self.chunk_id_list) != len(o.chunk_id_list):
            return False
        for i in range(len(self.chunk_id_list)):
            if self.chunk_id_list[i] != o.chunk_id_list[i]:
                return False
        return True

    def __hash__(self) -> int:
        return hash(self.chunk_id_list)

    def append(self, chunk_id):
        self.chunk_id_list.append(chunk_id)

    def serialize(self):
        io_stream = new_empty_buffer_stream()
        io_stream.write_unsigned_int(len(self.chunk_id_list))
        for chunk_id in self.chunk_id_list:
            io_stream.write_unsigned_int(chunk_id)
        return io_stream.buffer


class HashChunkList:

    def __init__(self):
        self.chunks = []

    def __len__(self):
        return len(self.chunks)

    def __iter__(self):
        return self.chunks.__iter__()

    def __getitem__(self, item):
        return self.chunks[item]

    def __str__(self):
        return str(self.chunks)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, HashChunkList):
            return False
        if len(self.chunks) != len(o.chunks):
            return False
        for i in range(len(self.chunks)):
            if self.chunks[i] != o.chunks[i]:
                return False
        return True

    def __hash__(self) -> int:
        return hash(self.chunks)

    def diff(self, old_hash_chunks) -> ChunkIdList:
        """
        Compare two HashChunkList object
        :param old_hash_chunks: other HashChunkList object
        :return: a list of changed chunk_id. If the length of old_hash_chunks is greater than self,
            return empty list indicating a full file change
            Currently this implementation only support additive changes detection, a empty list return means that
            we don't know how to handle this case, download the whole file instead.
        """
        changed_ids = ChunkIdList()
        self_len = len(self)
        old_len = len(old_hash_chunks)

        if old_len > self_len:
            return changed_ids

        c_id = 0
        while c_id < old_len:
            if self.chunks[c_id] != old_hash_chunks.chunks[c_id]:
                changed_ids.append(c_id)
            c_id += 1

        for _ in range(self_len - old_len):
            changed_ids.append(c_id)
            c_id += 1
        return changed_ids

    def append(self, hash_sum):
        self.chunks.append(hash_sum)

    def serialize(self):
        buf_stream = new_empty_buffer_stream()
        buf_stream.write_unsigned_int(len(self.chunks))
        for chunk_hash in self.chunks:
            buf_stream.write_string(chunk_hash)
        return buf_stream.buffer


def deserialize_hash_chunk_list_from_stream(io_stream: IOStream):
    chunks_len = io_stream.read_unsigned_int()
    chunks = HashChunkList()
    if chunks_len > 0:
        for i in range(chunks_len):
            chunk_hash, _ = io_stream.read_string()
            chunks.append(chunk_hash)
    return chunks


def deserialize_chunk_id_list_from_stream(io_stream: IOStream):
    id_list_len = io_stream.read_unsigned_int()
    id_list = ChunkIdList()
    for _ in range(id_list_len):
        id_list.append(io_stream.read_unsigned_int())
    return id_list
