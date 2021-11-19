import unittest

import left.file_table
from left.file_table import *


class MyTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ft = FileTable("share", auto_init_table=False)

        self.file_info_1 = FileInfo("share/1.txt", 2, "64ec88ca00b268e5ba1a35678a1b5316d212f4f366b2477232534a8aeca37f3c")
        self.ft.add_file_to_file_table(self.file_info_1)

        self.file_info_2 = FileInfo("share/测试/2.txt", 3,
                                    "8e28e54d601f0751922de24632c1e716b4684876255cf82304a9b19e89a9ccac")
        self.ft.add_file_to_file_table(self.file_info_2)

    def test_serialize_deserialize(self):
        bytes_buf = self.ft.serialize()

        new_ft = left.file_table.deserialize(bytes_buf)

        self.assertEqual(True, self.file_info_1.file_path in new_ft)
        self.assertEqual(True, self.file_info_1 == new_ft[self.file_info_1.file_path])

        self.assertEqual(True, self.file_info_1.file_path in new_ft)
        self.assertEqual(True, self.file_info_2 == new_ft[self.file_info_2.file_path])

    def test_diff(self):
        remote_ft = FileTable("share", auto_init_table=False)
        remote_ft.add_file_to_file_table(self.file_info_1)

        events = self.ft.diff(remote_ft)
        self.assertEqual(EVENT_SEND_NEW_FILE, events[0].event_id)
        self.assertEqual(events[0].file_info, self.file_info_2)


if __name__ == '__main__':
    unittest.main()
