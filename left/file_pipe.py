# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import threading

from concurrent_queue import DataQueue
from stream import IOStream
from logger import Logger


class FilePipe:
    BUF_SIZE = 5242880  # 1MB

    def __init__(self, input_stream: IOStream, output_stream, total_file_size: int, logger_name="FilePipe"):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.total_file_size = total_file_size

        self.data_queue = DataQueue(self.BUF_SIZE * 5)
        self.logger = Logger(logger_name)

        self.thread_input = threading.Thread(name="FilePipeInput", target=self._pump_file_in)
        self.thread_output = threading.Thread(name="FilePipeOutput", target=self._pump_file_out)

    def pump_file(self):
        self.thread_input.start()
        self.thread_output.start()

        self.thread_input.join()
        self.thread_output.join()

    def _pump_file_in(self):
        remain_sz = self.total_file_size
        while remain_sz > 0:

            # self.logger.log_verbose(f"input_stream.read() call, remain size: {remain_sz}, request read: {min(self.BUF_SIZE, remain_sz)}")
            buf = self.input_stream.read_unsafe(self.BUF_SIZE)
            # self.logger.log_verbose(f"input_stream.read() return, remaining size: {remain_sz}")
            remain_sz -= len(buf)
            self.data_queue.push(buf)

        self.logger.log_verbose("_pump_file_in return; Thread FilePipeInput exit")

    def _pump_file_out(self):
        remain_sz = self.total_file_size
        while remain_sz > 0:
            buf = self.data_queue.pop()
            sent = len(buf)
            # self.logger.log_verbose("output_stream.write() call")
            self.output_stream.write(buf)
            remain_sz -= sent
            # self.logger.log_verbose(f"output_stream.write() return, remain size: {remain_sz}")

        self.logger.log_verbose("_pump_file_out return; Thread FilePipeOutput exit")