# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

from struct import *

from stream import IOStream, new_empty_buffer_stream
from left_error import LeftError
from left_constants import *


class LeftPacket:
    def __init__(self, opcode: bytes):
        self.opcode = opcode
        self.target = None
        self.version = None
        self.name = None
        self.data = None

    def write_bytes(self, io_stream: IOStream):
        buf_stream = new_empty_buffer_stream()
        if self.target is not None:
            buf_stream.write(HEADER_F4_TARGET)
            buf_stream.write_length(self.target, 4)

        if self.version is not None:
            buf_stream.write(HEADER_F1_VERSION)
            buf_stream.write_length(self.version, 1)

        if self.name is not None:
            buf_stream.write(HEADER_VS_NAME)
            buf_stream.write_string(self.name)

        if self.data is not None:
            buf_stream.write(HEADER_F0_END_OF_HEADERS)
            buf_stream.write(self.data)

        io_stream.write(self.opcode)
        io_stream.write_unsigned_short(buf_stream.buf_len + 3)
        io_stream.write(buf_stream.buffer)


def read_packet_from_stream(stream: IOStream) -> LeftPacket:
    opcode = stream.read(1)
    packet = None
    if OPCODE_CONNECT <= opcode <= OPCODE_DOWNLOAD_FILE or opcode == OPCODE_SUCCESS or opcode == OPCODE_NOT_FOUND:
        packet = LeftPacket(opcode)

    if packet is None:
        raise LeftError(f"Illegal opcode {opcode}")

    unread_packet_len = stream.read(2)
    unread_packet_len = unpack("!H", unread_packet_len)[0]
    unread_packet_len -= 3

    while unread_packet_len > 0:
        header_id = stream.read(1)
        unread_packet_len = unread_packet_len - 1
        if header_id == HEADER_F1_VERSION:
            packet.version = stream.read(1)
            unread_packet_len -= 1
        elif header_id == HEADER_F4_TARGET:
            packet.target = unpack("4s", stream.read(4))[0]
            unread_packet_len -= 4
        elif header_id == HEADER_VS_NAME:
            packet.name, sz = stream.read_string()
            unread_packet_len -= sz
        elif header_id == HEADER_F0_END_OF_HEADERS:
            packet.data = stream.read(unread_packet_len)
            unread_packet_len = 0
        else:
            raise LeftError(f"Illegal header ID {header_id}")

    return packet
