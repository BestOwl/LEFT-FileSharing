import os.path
import socket
import threading

from left.file_pipe import FilePipe
from left.stream import FileStream, SocketStream

in_file_name = "../share_dummy_files/benchmark-500M.exe"
in_file_size = os.path.getsize(in_file_name)


def start_provider():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("", 30001))
    server_sock.listen()
    client_sock, address_port = server_sock.accept()
    with open(in_file_name, "rb") as in_file:
        pipe = FilePipe(FileStream(in_file), SocketStream(client_sock), in_file_size)
        pipe.pump_file()
    client_sock.close()
    server_sock.close()


def start_downloader():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 30001))
    with open("../share_dummy_tmp/test_pipe_transfer-500M.out", "wb") as out_file:
        pipe = FilePipe(SocketStream(sock), FileStream(out_file), in_file_size)
        pipe.pump_file()
    sock.close()


thread_provider = threading.Thread(target=start_provider)
thread_downloader = threading.Thread(target=start_downloader)

thread_provider.start()
thread_downloader.start()

thread_provider.join()
thread_downloader.join()
