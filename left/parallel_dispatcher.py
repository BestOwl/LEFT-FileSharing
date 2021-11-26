# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import threading

from concurrent_queue import ConcurrentQueue
from logger import Logger


class ParallelDispatcher:

    def __init__(self, max_degree_of_parallelism: int, thread_name="ParallelDispatcher",
                 new_share_execution_context_callback=None):
        self.degree_of_parallelism = max_degree_of_parallelism
        self.thread_name = thread_name
        self.new_share_execution_context_callback = new_share_execution_context_callback

        self.threads_lock = threading.Lock()
        self.threads = 0
        self.job_queue = ConcurrentQueue()
        self.logger = Logger("ParallelDispatcher")
        self.job_finished = threading.Event()

        self.dispatch_id_queue = ConcurrentQueue()
        for i in range(max_degree_of_parallelism):
            self.dispatch_id_queue.push(i)

    def execute(self, execute_callback, args=()):
        with self.threads_lock:
            if self.threads < self.degree_of_parallelism:
                self.logger.log_verbose("new thread for new job")
                dispatch_id = self.dispatch_id_queue.pop()
                self.logger.log_verbose(f"dispatch_id: {dispatch_id}")
                thread_exec = threading.Thread(name=f"{self.thread_name}-{dispatch_id}",
                                               target=self._execute_thread, args=[dispatch_id, execute_callback, args])
                self.threads += 1
                thread_exec.start()
            else:
                self.job_queue.push((execute_callback, args))

    def _execute_thread(self, dispatch_id: int, execute_callback, args: ()):
        self.logger.log_debug(f"DispatchThread-{dispatch_id} start first job")
        share_execution_context = None
        if self.new_share_execution_context_callback is not None:
            share_execution_context = self.new_share_execution_context_callback(dispatch_id)
        execute_callback(share_execution_context, *args)
        self.logger.log_debug(f"DispatchThread-{dispatch_id} job finished")

        while True:
            next_job = self.job_queue.pop()
            if next_job is not None:
                self.logger.log_debug(f"DispatchThread-{dispatch_id} continue with remaining job")
                next_job[0](share_execution_context, *next_job[1])
                self.logger.log_debug(f"DispatchThread-{dispatch_id} job finished")
            else:
                break

        with self.threads_lock:
            self.threads -= 1
            if self.threads == 0:
                self.job_finished.set()
            self.logger.log_debug(f"DispatchThread-{dispatch_id} exit")
            self.dispatch_id_queue.push(dispatch_id)

    def join(self):
        self.job_finished.wait()
        self.job_finished.clear()
