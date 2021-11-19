# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su


class LeftError(Exception):
    def __init__(self, message: str):
        self.message = message
