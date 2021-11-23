# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import unittest
from left.stream import BufferStream

def assert_read_foobar(test_case: unittest.TestCase, buf_stream: BufferStream):
    test_case.assertEqual(b"f", buf_stream.read(1))
    test_case.assertEqual(b"o", buf_stream.read(1))
    test_case.assertEqual(b"o", buf_stream.read(1))
    test_case.assertEqual(b"b", buf_stream.read(1))
    test_case.assertEqual(b"a", buf_stream.read(1))
    test_case.assertEqual(b"r", buf_stream.read(1))
    test_case.assertEqual(b"", buf_stream.read(1))

class MyTestCase(unittest.TestCase):

    def test_buffer_stream_read(self):
        buf = b"foobar"
        buf_stream = BufferStream(buf)
        assert_read_foobar(self, buf_stream)

    def test_buffer_stream_write(self):
        buf_stream = BufferStream(b"")
        buf_stream.write(b"foobar")
        assert_read_foobar(self, buf_stream)

    def test_buffer_stream_io(self):
        buf_stream = BufferStream(b"a")
        buf_stream.write(b"foobar")
        self.assertEqual(b"a", buf_stream.read(1))
        assert_read_foobar(self, buf_stream)

    def test_read_string_null_terminated(self):
        buf_stream = BufferStream(b"LEFT\x00")
        self.assertEqual("LEFT", buf_stream.read_string()[0])


if __name__ == '__main__':
    unittest.main()
