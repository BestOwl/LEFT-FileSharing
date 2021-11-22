# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

from struct import *

from stream import IOStream
from left_error import LeftError
from left_constants import *


class LeftPacket:
    def __init__(self, opcode: bytes):
        self.opcode = opcode
        self.target = None
        self.version = None
        self.data = None

    def to_bytes(self):
        sz_target = 0
        b_target = b""
        if self.target is not None:
            sz_target = calcsize("c4s")
            b_target = pack("c4s", HEADER_F4_TARGET, self.target)

        sz_version = 0
        b_version = b""
        if self.version is not None:
            sz_version = calcsize("cc")
            b_version = pack("cc", HEADER_F1_VERSION, self.version)

        sz_packet_len = calcsize("!H")
        sz_data = 0
        b_data = b""
        if self.data is not None:
            sz_data = len(self.data)
            b_data = pack(f"c{sz_data}s", HEADER_F0_END_OF_HEADERS, self.data)
            sz_data += 1

        total_len = 1 + sz_packet_len + sz_target + sz_version + sz_data
        return pack(f"c {sz_packet_len}s {sz_target}s {sz_version}s {sz_data}s",
                    self.opcode, pack("!H", total_len), b_target, b_version, b_data)


def read_packet_from_stream(stream) -> LeftPacket:
    opcode = stream.read(1)
    packet = None
    if OPCODE_CONNECT <= opcode <= OPCODE_SYNC_FILE_TABLE or OPCODE_SUCCESS >= opcode >= OPCODE_SUCCESS:
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
        elif header_id == HEADER_F0_END_OF_HEADERS:
            packet.data = stream.read(unread_packet_len)
            unread_packet_len = 0
        else:
            raise LeftError(f"Illegal header ID {header_id}")

    return packet
