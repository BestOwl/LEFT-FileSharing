# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su


OPCODE_CONNECT = b"\x80"
OPCODE_SYNC_FILE_TABLE = b"\x81"
OPCODE_DOWNLOAD_FILE = b"\x82"
OPCODE_FILE_EVENT = b"\x83"

OPCODE_SUCCESS = b"\xA0"
OPCODE_NOT_MODIFIED = b"\xA1"

OPCODE_NOT_FOUND = b"\xB4"

HEADER_F4_TARGET = b"\x46"
HEADER_F1_VERSION = b"\x76"
HEADER_F0_END_OF_HEADERS = b"\x48"
HEADER_VS_NAME = b"\x49"
