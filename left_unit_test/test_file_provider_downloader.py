# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import threading
import unittest

from left import file_helper
from left.file_downloader import FileDownloader
from left.file_provider import FileProvider
from left.stream import BufferStream, new_empty_buffer_stream, FileStream


def start_provider(provider):
    provider.provide_file()


def start_downloader(downloader):
    downloader.download_file()


class MyTestCase(unittest.TestCase):
    def test_provider_downloader_in_memory(self):
        in_mem_original_file_buffer = b"LoremIpsumissimplydummytextoftheprintingandtypesettingindustry.LoremIpsumhasbeentheindustry'sstandarddummytexteversincethe1500s,whenanunknownprintertookagalleyoftypeandscrambledittomakeatypespecimenbook.Ithassurvivednotonlyfivecenturies,butalsotheleapintoelectronictypesetting,remainingessentiallyunchanged.Itwaspopularisedinthe1960swiththereleaseofLetrasetsheetscontainingLoremIpsumpassages,andmorerecentlywithdesktoppublishingsoftwarelikeAldusPageMakerincludingversionsofLoremIpsum."
        in_mem_file_stream = BufferStream(in_mem_original_file_buffer)
        in_mem_transfer_stream = new_empty_buffer_stream()
        in_mem_write_file_stream = new_empty_buffer_stream()

        provider = FileProvider(in_mem_file_stream, in_mem_transfer_stream)
        thread_provider = threading.Thread(target=start_provider, args=[provider])
        thread_provider.start()

        downloader = FileDownloader(in_mem_write_file_stream, in_mem_transfer_stream, len(in_mem_original_file_buffer),
                                    None)
        thread_downloader = threading.Thread(target=start_downloader, args=[downloader])
        thread_downloader.start()

        thread_provider.join()
        print("provider thread exit")
        thread_downloader.join()
        print("downloader thread exit")
        self.assertEqual(in_mem_original_file_buffer, in_mem_write_file_stream.buffer)

    def test_downloader_download_real_file(self):
        original_file = FileStream("dummy_files/test_file_provider_downloader_test_file.txt", "rb")
        out_file = FileStream("dummy_files/test_file_provider_downloader_test_file.txt.out", "wb")
        downloader = FileDownloader(out_file, original_file,
                                    file_helper.get_file_size(
                                        "dummy_files/test_file_provider_downloader_test_file.txt"), None)
        downloader.download_file()
        original_file.close()
        out_file.close()
        self.assertEqual(file_helper.get_file_hash_md5("dummy_files/test_file_provider_downloader_test_file.txt"),
                         file_helper.get_file_hash_md5("dummy_files/test_file_provider_downloader_test_file.txt.out"))


if __name__ == '__main__':
    unittest.main()
