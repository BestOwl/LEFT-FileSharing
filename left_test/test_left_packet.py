# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import unittest

from left.left_packet import *


class MyTestCase(unittest.TestCase):
    def test_to_bytes(self):
        packet = LeftPacket(OPCODE_CONNECT)
        packet.target = b"LEFT"
        packet.version = b"\x10"
        self.assertEqual(b"\x80\x00\x0A\x46\x4C\x45\x46\x54\x76\x10", packet.to_bytes())  # expected, actual


if __name__ == '__main__':
    unittest.main()
