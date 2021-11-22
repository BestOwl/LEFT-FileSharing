# import unittest
#
#
# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)  # add assertion here
#
#
# if __name__ == '__main__':
#     unittest.main()
import threading
import time

from left.concurrent_queue import ConcurrentQueue
from left.file_table import FileTable
from left.watch_dog import WatchDog

ft = FileTable("share")
event_queue = ConcurrentQueue()
watchdog = WatchDog(ft, event_queue)


def start_watch_dog():
    watchdog.start()


threading.Thread(target=start_watch_dog).start()
while True:
    event = event_queue.pop()
    if event is not None:
        print(f"{event.event_id} {event.file_info.file_path}")
    else:
        time.sleep(0.05)