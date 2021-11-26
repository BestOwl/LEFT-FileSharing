# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import os.path
import threading
import socket
import time

from left.concurrent_queue import ConcurrentQueue
from left.logger import *
from left.stream import FileStream, SocketStream, IOStream


def main():
    thread_server = threading.Thread(name="FileServer", target=start_file_server)
    thread_client = threading.Thread(name="FileClient", target=start_file_client)
    thread_server.start()
    thread_client.start()
    thread_server.join()
    thread_client.join()


def start_file_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("", 30001))
    server_sock.listen()
    client_sock, address_port = server_sock.accept()

    with open("../share_dummy_files/benchmark-500M.exe", "rb") as f:
        provider = NaiveFileProvider(FileStream(f), SocketStream(client_sock))
        file_provider_benchmark(provider)

    time.sleep(1)

    with open("../share_dummy_files/benchmark-500M.exe", "rb") as f:
        provider = QueuedFileProvider(FileStream(f), SocketStream(client_sock))
        file_provider_benchmark(provider)


def start_file_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 30001))
    with open("../share_dummy_tmp/classic.out", "wb") as f:
        downloader = NaiveFileDownloader(FileStream(f), SocketStream(sock),
                                         os.path.getsize("../share_dummy_files/benchmark-500M.exe"), None)
        file_downloader_benchmark(downloader)

    time.sleep(1)

    with open("../share_dummy_tmp/classic.out", "wb") as f:
        downloader = QueuedFileDownloader(FileStream(f), SocketStream(sock),
                                          os.path.getsize("../share_dummy_files/benchmark-500M.exe"), None)
        file_downloader_benchmark(downloader)


def file_provider_benchmark(provider):
    print("File provider started")
    time_start = time.perf_counter()
    provider.provide_file()
    time_end = time.perf_counter()
    print(f"File provider finished: {time_end - time_start} ms")


def file_downloader_benchmark(downloader):
    print("Downloader start")
    time_start = time.perf_counter()
    downloader.download_file()
    time_end = time.perf_counter()
    print(f"Downloader finished: {time_end - time_start} ms")


FILE_TRANSFER_BUFFER_SIZE = 20971520  # 20MB


class FileDownloader:
    def __init__(self, file_stream: IOStream, io_stream: IOStream, total_file_size: int, download_progress_callback):
        self.file_stream = file_stream
        self.io_stream = io_stream
        self.total_file_size = total_file_size
        self.download_progress_callback = download_progress_callback

    def download_file(self):
        pass


class FileProvider:

    def __init__(self, file_stream: IOStream, io_stream: IOStream):
        self.file_stream = file_stream
        self.io_stream = io_stream

    def provide_file(self):
        pass


class NaiveFileDownloader(FileDownloader):

    def download_file(self):
        total_receive_sz = 0
        while total_receive_sz < self.total_file_size:
            # print(f"{CONSOLE_COLOR_GREEN}[{time.perf_counter()}] io_stream read {CONSOLE_COLOR_RESET}")
            buf = self.io_stream.read(FILE_TRANSFER_BUFFER_SIZE)
            # print(f"{CONSOLE_COLOR_GREEN}[{time.perf_counter()}] io_stream return {CONSOLE_COLOR_RESET}")
            total_receive_sz += len(buf)

            if self.download_progress_callback is not None:
                self.download_progress_callback(total_receive_sz, self.total_file_size)
            # print(f"{CONSOLE_COLOR_GREEN}[{time.perf_counter()}] file_stream write {CONSOLE_COLOR_RESET}")
            self.file_stream.write(buf)
            # print(f"{CONSOLE_COLOR_GREEN}[{time.perf_counter()}] file_stream return {CONSOLE_COLOR_RESET}")


class NaiveFileProvider(FileProvider):

    def provide_file(self):
        while True:
            # print(f"{CONSOLE_COLOR_BLUE} [{time.perf_counter()}] file_stream read {CONSOLE_COLOR_RESET}")
            buf = self.file_stream.read(FILE_TRANSFER_BUFFER_SIZE)
            # print(f"{CONSOLE_COLOR_BLUE} [{time.perf_counter()}] file_stream return {CONSOLE_COLOR_RESET}")
            if buf == b"":
                break
            else:
                # print(f"{CONSOLE_COLOR_BLUE} [{time.perf_counter()}] sock_stream write {CONSOLE_COLOR_RESET}")
                self.io_stream.write(buf)
                # print(f"{CONSOLE_COLOR_BLUE} [{time.perf_counter()}] sock_stream return {CONSOLE_COLOR_RESET}")


class QueuedFileProvider(FileProvider):
    BUF_SIZE = 4096

    def __init__(self, file_stream: IOStream, io_stream: IOStream):
        super().__init__(file_stream, io_stream)
        self.data_queue = ConcurrentQueue()
        self._finished = False
        self.thread_read_file = threading.Thread(name="ReadFile", target=self.read_bytes_from_file)
        self.thread_write_sock = threading.Thread(name="WriteSock", target=self.write_bytes_to_stream)

    def provide_file(self):
        self.thread_read_file.start()
        self.thread_write_sock.start()

        self.thread_read_file.join()
        self.thread_write_sock.join()

    def read_bytes_from_file(self):
        while True:
            buf = self.file_stream.read(FILE_TRANSFER_BUFFER_SIZE)
            if buf == b"":
                break
            self.data_queue.push(buf)
        self._finished = True

    def write_bytes_to_stream(self):
        while not self._finished:
            buf = self.data_queue.pop()
            if buf is not None:
                self.io_stream.write(buf)


class QueuedFileDownloader(FileDownloader):
    BUF_SIZE = 4096

    def __init__(self, file_stream: IOStream, io_stream: IOStream, total_file_size: int, download_progress_callback):
        super().__init__(file_stream, io_stream, total_file_size, download_progress_callback)
        self.data_queue = ConcurrentQueue()
        self._finished = False
        self.thread_read_sock = threading.Thread(name="ReadSock", target=self.read_bytes_from_stream)
        self.thread_write_file = threading.Thread(name="WriteFile", target=self.write_bytes_to_file)

    def download_file(self):
        self.thread_read_sock.start()
        self.thread_write_file.start()

        self.thread_read_sock.join()
        self.thread_write_file.join()

    def read_bytes_from_stream(self):
        while True:
            buf = self.io_stream.read(FILE_TRANSFER_BUFFER_SIZE)
            if buf == b"":
                break
            self.data_queue.push(buf)
        self._finished = True

    def write_bytes_to_file(self):
        while not self._finished:
            buf = self.data_queue.pop()
            if buf is not None:
                self.file_stream.write(buf)


if __name__ == "__main__":
    main()
