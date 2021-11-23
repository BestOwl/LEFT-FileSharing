# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

from left_constants import FILE_TRANSFER_BUFFER_SIZE
from stream import IOStream


class FileProvider:

    def __init__(self, file_stream: IOStream, io_stream: IOStream):
        self.file_stream = file_stream
        self.io_stream = io_stream

    def provide_file(self):
        while True:
            buf = self.file_stream.read(FILE_TRANSFER_BUFFER_SIZE)
            if buf == b"":
                break
            else:
                self.io_stream.write(buf)
