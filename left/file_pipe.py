# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import threading

from concurrent_queue import ConcurrentQueue
from stream import IOStream
from logger import Logger


class FilePipe:
    BUF_SIZE = 20971520

    def __init__(self, input_stream: IOStream, output_stream, total_file_size: int):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.total_file_size = total_file_size

        self.data_queue = ConcurrentQueue()
        self.logger = Logger("FilePipe")

        self.thread_input = threading.Thread(name="FilePipeInput", target=self._pump_file_in)
        self.thread_output = threading.Thread(name="FilePipeOutput", target=self._pump_file_out)

    def pump_file(self):
        self.thread_input.start()
        self.thread_output.start()

        self.thread_input.join()
        self.thread_output.join()

    def _pump_file_in(self):
        total_input_size = 0
        while total_input_size <= self.total_file_size:
            buf = self.input_stream.read(self.BUF_SIZE)
            if buf == b"":
                break
            total_input_size += len(buf)
            self.data_queue.push(buf)
        self.logger.log_verbose("_pump_file_in return; Thread FilePipeInput exit")

    def _pump_file_out(self):
        total_receive_sz = 0
        while total_receive_sz < self.total_file_size:
            buf = self.data_queue.pop()
            if buf is not None:
                total_receive_sz += len(buf)
                self.output_stream.write(buf)
        self.logger.log_verbose("_pump_file_out return; Thread FilePipeOutput exit")