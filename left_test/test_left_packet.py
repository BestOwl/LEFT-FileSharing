# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import unittest

from left.left_packet import *
from left.stream import BufferStream, new_empty_buffer_stream


class MyTestCase(unittest.TestCase):
    def test_to_bytes(self):
        packet = LeftPacket(OPCODE_CONNECT)
        packet.target = b"LEFT"
        packet.version = b"\x10"
        packet.data = b"f"
        io_stream = new_empty_buffer_stream()
        packet.write_bytes(io_stream)
        self.assertEqual(b"\x80\x00\x0C\x46\x4C\x45\x46\x54\x76\x10" + HEADER_F0_END_OF_HEADERS + b"f",
                         io_stream.buffer)  # expected, actual

    def test_opcode_only_header(self):
        packet = LeftPacket(OPCODE_SUCCESS)
        buf_stream = new_empty_buffer_stream()
        packet.write_bytes(buf_stream)

        self.assertEqual(OPCODE_SUCCESS + b"\x00\x03", buf_stream.buffer)

        new_packet = read_packet_from_stream(buf_stream)
        self.assertEqual(OPCODE_SUCCESS, new_packet.opcode)

    def test_data_integrity(self):
        packet = LeftPacket(OPCODE_CONNECT)
        packet.target = b"TEST"
        packet.version = b"\xA0"
        packet.data = b"foobar"

        io_stream = new_empty_buffer_stream()
        packet.write_bytes(io_stream)
        remote_packet = read_packet_from_stream(io_stream)
        self.assertEqual(OPCODE_CONNECT, remote_packet.opcode)
        self.assertEqual(b"TEST", remote_packet.target)
        self.assertEqual(b"\xA0", remote_packet.version)
        self.assertEqual(b"foobar", remote_packet.data)


if __name__ == '__main__':
    unittest.main()
