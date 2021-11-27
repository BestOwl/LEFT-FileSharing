# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

# TODO: remove inspect module before submission
import inspect
import os

LOG_LEVEL_ERROR = 0
LOG_LEVEL_WARNING = 1
LOG_LEVEL_INFO = 2
LOG_LEVEL_DEBUG = 3
LOG_LEVEL_VERBOSE = 4

CURRENT_LOG_LEVEL = LOG_LEVEL_INFO

CONSOLE_COLOR_RED = "\033[1;31m"
CONSOLE_COLOR_BLUE = "\033[1;34m"
CONSOLE_COLOR_CYAN = "\033[1;36m"
CONSOLE_COLOR_GREEN = "\033[0;32m"
CONSOLE_COLOR_RESET = "\033[0;0m"
CONSOLE_COLOR_BOLD = "\033[;1m"
CONSOLE_COLOR_REVERSE = "\033[;7m"


class Logger:

    def __init__(self, logger_name: str):
        self.logger_name = logger_name

    def log_info(self, message: str):
        if CURRENT_LOG_LEVEL >= LOG_LEVEL_INFO:
            print(f"[INFO] {self.logger_name}#      {message}")

    def log_warning(self, message: str):
        if CURRENT_LOG_LEVEL >= LOG_LEVEL_WARNING:
            print(f"{CONSOLE_COLOR_CYAN}[WARNING] {self.logger_name}#    {message} {CONSOLE_COLOR_RESET}")

    def log_error(self, message: str):
        if CURRENT_LOG_LEVEL >= LOG_LEVEL_ERROR:
            print(f"{CONSOLE_COLOR_RED}[ERROR] {self.logger_name}#    {message} {CONSOLE_COLOR_RESET}")

    def log_debug(self, message: str):
        if CURRENT_LOG_LEVEL >= LOG_LEVEL_DEBUG:
            print(f"[DEBUG] {self.logger_name}#    {message}")

    def log_verbose(self, message: str):
        if CURRENT_LOG_LEVEL >= LOG_LEVEL_VERBOSE:
            caller = inspect.stack()[1]
            print(f"{CONSOLE_COLOR_BLUE}[VERBOSE] {self.logger_name} {caller.function} L{caller.lineno}#    {message} "
                  f"{CONSOLE_COLOR_RESET}")
            pass
