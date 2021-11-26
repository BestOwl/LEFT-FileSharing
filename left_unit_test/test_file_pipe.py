# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su
import os.path
import unittest

from left import file_helper
from left.file_pipe import FilePipe
from left.stream import FileStream


class MyTestCase(unittest.TestCase):
    # TODO: currently FilePipe can not be tested in-memory because in-memory BufferStream is non-blocking

    def test_file_pipe_pump_real_file(self):
        source_file_name = "../share_dummy_files/test_file_provider_downloader_test_file.txt"
        out_file_name = "../share_dummy_tmp/test_file_provider_downloader_test_file.txt.out"

        with open(source_file_name, "rb") as source, open(out_file_name, "wb") as out:
            source_stream = FileStream(source)
            out_stream = FileStream(out)
            file_size = os.path.getsize(source_file_name)
            pipe = FilePipe(source_stream, out_stream, file_size)
            pipe.pump_file()

        self.assertEqual(file_helper.get_file_hash_md5(source_file_name), file_helper.get_file_hash_md5(out_file_name))

    def test_file_pump_real_large_file_500m(self):
        source_file_name = "../share_dummy_files/benchmark-500M.exe"
        out_file_name = "../share_dummy_tmp/500m.out"

        with open(source_file_name, "rb") as source, open(out_file_name, "wb") as out:
            source_stream = FileStream(source)
            out_stream = FileStream(out)
            file_size = os.path.getsize(source_file_name)
            pipe = FilePipe(source_stream, out_stream, file_size)
            pipe.pump_file()

        self.assertEqual(file_helper.get_file_hash_md5(source_file_name), file_helper.get_file_hash_md5(out_file_name))



if __name__ == '__main__':
    unittest.main()
