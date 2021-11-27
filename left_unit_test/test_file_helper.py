# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import unittest
import left.file_helper as file_helper
from left import file_info


class MyTestCase(unittest.TestCase):
    def test_get_file_hash_md5(self):
        self.assertEqual("ee6349072db89fb90ec9e25d07bfcb3a", file_helper.get_file_hash_md5(
            "../share_dummy_files/1.txt"))
        self.assertEqual("3e25960a79dbc69b674cd4ec67a72c62", file_helper.get_file_hash_md5(
            "../share_dummy_files/2.txt"))
        self.assertEqual("cdfb631eace07df242e8f43b089dae10", file_helper.get_file_hash_md5(
            "../share_dummy_files/3.ova"))

    def test_is_hidden_file(self):
        self.assertTrue(file_helper.is_hidden_file("/tmp/.haha"))
        self.assertTrue(file_helper.is_hidden_file("/tmp/..haha."))
        self.assertTrue(file_helper.is_hidden_file("/.1"))
        self.assertTrue(file_helper.is_hidden_file(".1"))
        self.assertTrue(file_helper.is_hidden_file("test_file_helper_test_files/.test"))
        self.assertTrue(file_helper.is_hidden_file("test_file_helper_test_files/.test.txt"))
        self.assertTrue(file_helper.is_hidden_file("test_file_helper_test_files/haha/.dummy.txt"))

        self.assertFalse(file_helper.is_hidden_file("/tmp/haha"))
        self.assertFalse(file_helper.is_hidden_file("/tmp/haha."))
        self.assertFalse(file_helper.is_hidden_file("/1"))
        self.assertFalse(file_helper.is_hidden_file("1"))

    def test_is_hidden_folder(self):
        self.assertTrue(file_helper.is_hidden_folder("/home/haha/.ssh/"))
        self.assertTrue(file_helper.is_hidden_folder("/home/haha/.ssh../"))
        self.assertTrue(file_helper.is_hidden_folder("/.ssh/"))
        self.assertTrue(file_helper.is_hidden_folder(".ssh/"))

        self.assertFalse(file_helper.is_hidden_folder("/home/haha/ssh/"))
        self.assertFalse(file_helper.is_hidden_folder("/home/haha/ssh../"))
        self.assertFalse(file_helper.is_hidden_folder("/ssh/"))
        self.assertFalse(file_helper.is_hidden_folder("ssh/"))

    def test_scan_path_tree_ignore_hidden(self):
        entry_list = []
        for dir_entry in file_helper.scan_path_tree("test_file_helper_test_files", ignore_hidden_file_or_folder=True):
            path = file_info.get_normalized_file_path(dir_entry.path)
            print(path)
            entry_list.append(path)
        entry_list.remove("test_file_helper_test_files/test.txt")
        entry_list.remove("test_file_helper_test_files/test")
        entry_list.remove("test_file_helper_test_files/haha/dummy.txt")
        entry_list.remove("test_file_helper_test_files/README.md")
        self.assertEqual(0, len(entry_list))


if __name__ == '__main__':
    unittest.main()
