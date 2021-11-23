# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import threading

from concurrent_queue import ConcurrentQueue
from logger import Logger


class ParallelDispatcher:

    def __init__(self, degree_of_parallelism: int, thread_name="ParallelDispatcher"):
        self.degree_of_parallelism = degree_of_parallelism
        self.thread_name = thread_name
        self.threads_lock = threading.Lock()
        self.threads = 0
        self.job_queue = ConcurrentQueue()
        self.logger = Logger("ParallelDispatcher")
        self.job_finished = threading.Event()

    def execute(self, execute_callback, args=()):
        with self.threads_lock:
            if self.threads < self.degree_of_parallelism:
                self.logger.log_verbose("new thread for new job")
                dispatch_id = self.threads
                self.logger.log_verbose(f"dispatch_id: {dispatch_id}")
                thread_exec = threading.Thread(name=f"{self.thread_name}-{dispatch_id}",
                                               target=self._execute_thread, args=[dispatch_id, execute_callback, args])
                self.threads += 1
                thread_exec.start()
            else:
                self.job_queue.push((execute_callback, args))

    def _execute_thread(self, dispatch_id: int, execute_callback, args: ()):
        self.logger.log_debug(f"DispatchThread-{dispatch_id} start first job")
        execute_callback(*args)
        self.logger.log_debug(f"DispatchThread-{dispatch_id} job finished")

        while True:
            next_job = self.job_queue.pop()
            if next_job is not None:
                self.logger.log_debug(f"DispatchThread-{dispatch_id} continue with remaining job")
                next_job[0](*next_job[1])
                self.logger.log_debug(f"DispatchThread-{dispatch_id} job finished")
            else:
                break

        with self.threads_lock:
            self.threads -= 1
        if self.threads == 0:
            self.job_finished.set()
        self.logger.log_debug(f"DispatchThread-{dispatch_id} exit")

    def join(self):
        self.job_finished.wait()
        self.job_finished.clear()
