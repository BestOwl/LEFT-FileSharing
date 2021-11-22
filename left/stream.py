# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import socket


class IOStream:

    def read(self, size: int) -> bytes:
        pass

    def read_string_null_terminated(self, encoding="utf-8") -> str:
        b_str = b""
        while True:
            b_read = self.read(1)
            if b_read == b"":
                break

            if b_read == b"\x00":
                break
            b_str += b_read

        if b_str != b"":
            return str(b_str, "utf-8")

    def write(self, buffer: bytes):
        pass


class SocketStream(IOStream):

    def __init__(self, sock: socket):
        self.sock = sock

    def read(self, size: int):
        return self.sock.recv(size)

    def write(self, buffer: bytes):
        self.sock.send(buffer)


class BufferStream(IOStream):

    def __init__(self, buffer: bytes):
        self.buffer = buffer
        self.buf_len = len(buffer)
        self.read_pos = 0

    def read(self, size: int) -> bytes:
        if self.read_pos + size <= self.buf_len:
            ret = self.buffer[self.read_pos:self.read_pos + size]
            self.read_pos += size
            return ret
        else:
            return b""

    def write(self, buffer: bytes):
        self.buffer += buffer
        self.buf_len += len(buffer)
