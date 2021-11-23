# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import unittest

from file_info import FileInfo
from left.file_event import FileEventList, FileEvent, EVENT_SEND_NEW_FILE, deserialize_file_event_list_from_stream
from left.stream import BufferStream


class MyTestCase(unittest.TestCase):
    def test_file_event_list_serialize_deserialize(self):
        f_event_list = FileEventList()
        f_info = FileInfo("share/1.txt", 1, "1")
        f_event_list.append(FileEvent(EVENT_SEND_NEW_FILE, f_info))

        buf = f_event_list.serialize()
        buf_stream = BufferStream(buf)
        f_event_list_new = deserialize_file_event_list_from_stream(buf_stream)

        self.assertEqual(EVENT_SEND_NEW_FILE, f_event_list_new[0].event_id)
        self.assertEqual(f_info, f_event_list_new[0].file_info)


if __name__ == '__main__':
    unittest.main()
