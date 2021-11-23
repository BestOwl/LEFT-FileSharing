# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import unittest
import left.file_helper as file_helper


class MyTestCase(unittest.TestCase):
    def test_get_file_hash_md5(self):
        self.assertEqual("ee6349072db89fb90ec9e25d07bfcb3a", file_helper.get_file_hash_md5(
            "../left_test/dummy_files/1.txt"))
        self.assertEqual("3e25960a79dbc69b674cd4ec67a72c62", file_helper.get_file_hash_md5(
            "../left_test/dummy_files/2.txt"))
        self.assertEqual("cdfb631eace07df242e8f43b089dae10", file_helper.get_file_hash_md5(
            "../left_test/dummy_files/3.ova"))


if __name__ == '__main__':
    unittest.main()
