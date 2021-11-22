# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import unittest

from left.file_info import FileInfo


class MyTestCase(unittest.TestCase):
    def test_file_info_different_path_separator(self):
        f1 = FileInfo("share/1.txt", 1, "1")
        f2 = FileInfo("share\\1.txt", 1, "1")

        self.assertTrue(f1 == f2)


if __name__ == '__main__':
    unittest.main()
