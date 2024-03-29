# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import threading

from concurrent_queue import DataQueue
from stream import IOStream
from logger import Logger


class FilePipe:
    BUF_SIZE = 5242880  # 1MB

    def __init__(self, name="FilePipe"):
        self.name = name

        self.input_stream = None
        self.output_stream = None
        self.total_file_size = None

        self.data_queue = DataQueue(self.BUF_SIZE * 5)
        self.logger = Logger(name)

        self.thread_output = threading.Thread(name="FilePipeOutput", target=self._pump_file_out)

        self._start_wait = threading.Event()
        self._end_wait = threading.Event()
        self._is_disposed = False

        self.thread_output.start()

    def dispose(self):
        self._is_disposed = True
        self._start_wait.set()

    def pump_file(self, input_stream: IOStream, output_stream: IOStream, total_file_size: int):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.total_file_size = total_file_size

        self._end_wait.clear()

        self._start_wait.set()
        self._start_wait.clear()

        self._pump_file_in()
        self._end_wait.wait()

    def _pump_file_in(self):
        remain_sz = self.total_file_size
        while remain_sz > 0:

            # self.logger.log_verbose(f"input_stream.read() call, remain size: {remain_sz}, request read: {min(self.BUF_SIZE, remain_sz)}")

            buf = self.input_stream.read(min(self.BUF_SIZE, remain_sz))
            # TODO: can not use read_unsafe() here, will cause bug, don't know why yet, fix it later

            # self.logger.log_verbose(f"input_stream.read() return, remaining size: {remain_sz}")
            remain_sz -= len(buf)
            self.data_queue.push(buf)

        self.logger.log_verbose("_pump_file_in return;")

    def _pump_file_out(self):
        while not self._is_disposed:
            self._start_wait.wait()
            if self._is_disposed:
                self._end_wait.set()
                break

            remain_sz = self.total_file_size
            while remain_sz > 0:
                buf = self.data_queue.pop()
                sent = len(buf)
                # self.logger.log_verbose("output_stream.write() call")
                self.output_stream.write(buf)
                remain_sz -= sent
                # self.logger.log_verbose(f"output_stream.write() return, remain size: {remain_sz}")

            self._end_wait.set()

        self.logger.log_verbose(f"_pump_file_out return; Thread {self.name} exit")