# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import unittest

from left.left_packet import *
from left.stream import BufferStream


class MyTestCase(unittest.TestCase):
    def test_to_bytes(self):
        packet = LeftPacket(OPCODE_CONNECT)
        packet.target = b"LEFT"
        packet.version = b"\x10"
        packet.data = b"f"
        self.assertEqual(b"\x80\x00\x0C\x46\x4C\x45\x46\x54\x76\x10" + HEADER_F0_END_OF_HEADERS + b"f",
                         packet.to_bytes())  # expected, actual

    def test_data_integrity(self):
        packet = LeftPacket(OPCODE_CONNECT)
        packet.target = b"TEST"
        packet.version = b"\xA0"
        packet.data = b"foobar"

        buf = packet.to_bytes()
        remote_packet = read_packet_from_stream(BufferStream(buf))
        self.assertEqual(OPCODE_CONNECT, remote_packet.opcode)
        self.assertEqual(b"TEST", remote_packet.target)
        self.assertEqual(b"\xA0", remote_packet.version)
        self.assertEqual(b"foobar", remote_packet.data)


if __name__ == '__main__':
    unittest.main()
