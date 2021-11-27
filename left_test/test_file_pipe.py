import os.path

from left.file_pipe import FilePipe
from left.stream import FileStream

in_file_name = "../share_dummy_files/benchmark-500M.exe"

total_file_size = os.path.getsize(in_file_name)

with open(in_file_name, "rb") as in_file, \
        open("../share_dummy_tmp/demo-500M.exe", "wb") as out_file:
    pipe = FilePipe(FileStream(in_file), FileStream(out_file), total_file_size)
    pipe.pump_file()
