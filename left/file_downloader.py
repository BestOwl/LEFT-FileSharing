# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

from stream import IOStream
from left_constants import FILE_TRANSFER_BUFFER_SIZE


class FileDownloader:

    def __init__(self, file_stream: IOStream, io_stream: IOStream, total_file_size: int, download_progress_callback):
        self.file_stream = file_stream
        self.io_stream = io_stream
        self.total_file_size = total_file_size
        self.download_progress_callback = download_progress_callback

    def download_file(self):
        total_receive_sz = 0
        while total_receive_sz < self.total_file_size:
            buf = self.io_stream.read(FILE_TRANSFER_BUFFER_SIZE)
            total_receive_sz += len(buf)

            if self.download_progress_callback is not None:
                self.download_progress_callback(total_receive_sz, self.total_file_size)
            self.file_stream.write(buf)
