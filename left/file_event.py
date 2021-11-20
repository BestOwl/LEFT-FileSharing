# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

from file_info import FileInfo

EVENT_UPDATE_MTIME = b"\xD0"
EVENT_SEND_NEW_FILE = b"\xD1"
EVENT_RECEIVE_NEW_FILE = b"\xD2"
EVENT_SEND_MODIFIED_FILE = b"\xD3"
EVENT_RECEIVE_MODIFIED_FILE = b"\xD4"
EVENT_REMOVE_FILE = b"\xD5"


class FileEvent:

    def __init__(self, event_id: bytes, file_info: FileInfo):
        self.event_id = event_id
        self.file_info = file_info
