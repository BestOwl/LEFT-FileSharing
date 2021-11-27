# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su


FILE_TRANSFER_BUFFER_SIZE = 20971520  # 20MB

OPCODE_CONNECT = b"\x80"
OPCODE_SYNC_FILE_TABLE = b"\x81"
OPCODE_DOWNLOAD_FILE = b"\x82"
OPCODE_FILE_EVENT = b"\x83"
OPCODE_DOWNLOAD_FILE_BYE = b"\x84"
OPCODE_DOWNLOAD_FILE_CONNECT = b"\x85"

OPCODE_SUCCESS = b"\xA0"
OPCODE_CONTINUE = b"\xA1"

OPCODE_NOT_MODIFIED = b"\xB0"
OPCODE_NOT_FOUND = b"\xB4"


def is_legal_opcode(opcode):
    return OPCODE_CONNECT <= opcode <= OPCODE_DOWNLOAD_FILE_CONNECT or OPCODE_SUCCESS <= opcode <= OPCODE_CONTINUE \
           or OPCODE_NOT_MODIFIED <= opcode <= OPCODE_NOT_FOUND


HEADER_F4_TARGET = b"\x46"
HEADER_F1_VERSION = b"\x76"
HEADER_F0_END_OF_HEADERS = b"\x48"
HEADER_VS_NAME = b"\x49"
