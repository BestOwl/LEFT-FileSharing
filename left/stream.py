# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import socket
import struct


class IOStream:

    def read(self, size: int) -> bytes:
        pass

    def read_string(self, encoding="utf-8") -> (str, int):
        """
        Read null-terminated string from IOStream
        :param encoding: encoding of the string bytes
        :return: string, and the number of bytes read
        """
        read_sz = 0
        b_str = b""
        while True:
            b_read = self.read(1)
            if b_read == b"":
                break
            read_sz += 1

            if b_read == b"\x00":
                break
            b_str += b_read

        if b_str != b"":
            return str(b_str, "utf-8"), read_sz
        else:
            return None, 0

    def write_string(self, string: str, encoding="utf-8"):
        self.write(bytes(string, encoding="utf-8"))
        self.write(b"\x00")

    def write_unsigned_short(self, num: int):
        """
        Write number as unsigned short in Big-Endian
        :param num: number
        """
        self.write(struct.pack("!H", num))

    def read_unsigned_short(self) -> int:
        """
        Read Big-Endian unsigned short from stream
        :return: number
        """
        return struct.unpack("!H", self.read(2))[0]

    def write_unsigned_int(self, num: int):
        """
        Write number as unsigned int in Big-Endian
        :param num: number
        """
        self.write(struct.pack("!I", num))

    def read_unsigned_int(self) -> int:
        """
        Read Big-Endian unsigned int from stream
        :return:
        """
        return struct.unpack("!I", self.read(4))[0]

    def write_unsigned_long_long(self, num: int):
        """
        Write number as unsigned long long in Big-Endian
        :param num: number
        """
        self.write(struct.pack("!Q", num))

    def read_unsigned_long_long(self) -> int:
        """
        Read Big-Endian unsigned long long from stream
        :return: number
        """
        return struct.unpack("!Q", self.read(8))[0]

    def write(self, buffer: bytes):
        pass

    def write_length(self, buffer: bytes, length: int):
        self.write(buffer[0:length])


class SocketStream(IOStream):

    def __init__(self, sock: socket):
        self.sock = sock

    def read(self, size: int):
        buf = bytearray(size)
        view = memoryview(buf)
        while size > 0:
            sz_read = self.sock.recv_into(view, size)
            if sz_read == 0:
                return b""

            view = view[sz_read:]
            size -= sz_read
        return bytes(buf)

    def write(self, buffer: bytes):
        # sz = len(buffer)
        # view = memoryview(buffer)
        # while sz > 0:
        #     sent = self.sock.send(view)
        #     sz -= sent
        self.sock.sendall(buffer)


class BufferStream(IOStream):

    def __init__(self, buffer: bytes):
        self.buffer = buffer
        self.buf_len = len(buffer)
        self.read_pos = 0

    def read(self, size: int) -> bytes:
        if self.read_pos < self.buf_len:
            actual_read_size = size
            if self.read_pos + size > self.buf_len:
                actual_read_size = self.buf_len - self.read_pos
            ret = self.buffer[self.read_pos:self.read_pos + size]
            self.read_pos += actual_read_size
            return ret
        else:
            return b""

    def write(self, buffer: bytes):
        self.buffer += buffer
        self.buf_len += len(buffer)


class FileStream(IOStream):

    def __init__(self, file_io):
        self.file_io = file_io

    def read(self, size: int) -> bytes:
        return self.file_io.read(size)

    def write(self, buffer: bytes):
        self.file_io.write(buffer)


def new_empty_buffer_stream() -> BufferStream:
    return BufferStream(b"")
