import unittest

from left.hash_chunk_list import *
from left.stream import BufferStream


class HashChunkListTestCase(unittest.TestCase):
    hash_chunks_1 = HashChunkList()
    hash_chunks_1.chunks = [
        "a2eee959f922d75e7762a259f8b06bf0",
        "610cfa54d9c986bdf4e8faf62ea4e964",
        "941d2cb16365e88649fb1648b334d0f2",
        "6dc16bf9e9dc3dc2f1eba57c4ef8eea5",
        "f5afc0afc18c46f6f4e53ef163e751aa",
        "db7f9794aa4c8444c592560d4b03f6e3",
        "300bc7811ade1f71a6046ec958cab7dc",
        "b80ebb24d128b3100007eba2f283a52a",
        "78882f17260904c356dcd3bd11cd242f",
        "a8ff7bb87ff92a6ecceefdf8a6811e33",
        "5254bbdd6c192aec0dab4246f2c0c8ae",
        "28e5826458f04a9c233f404979f6151e",
        "c8d50578e07c8537916d26a8fc551795",
        "0c14ff88d5f697122d1e04d99255b19b",
        "e29d4a43e71a7b0324e882b7f6635958",
        "e0d47f14f0119b8ed1931091b350c589",
        "d9f5ff6ed42ab4a81ac20cbc0d6f86d3",
        "9246bc7a518d4aa5f54b7f12ba080ebd",
        "66f19193ddef6ff8b973f20fb033c81e",
        "30b1021016ff433dbf3f2b3fa89849a0"
    ]

    def test_eq(self):
        hash_chunks_2 = HashChunkList()
        hash_chunks_2.chunks = [
            "a2eee959f922d75e7762a259f8b06bf0",
            "610cfa54d9c986bdf4e8faf62ea4e964",
            "941d2cb16365e88649fb1648b334d0f2",
            "6dc16bf9e9dc3dc2f1eba57c4ef8eea5",
            "f5afc0afc18c46f6f4e53ef163e751aa",
            "db7f9794aa4c8444c592560d4b03f6e3",
            "300bc7811ade1f71a6046ec958cab7dc",
            "b80ebb24d128b3100007eba2f283a52a",
            "78882f17260904c356dcd3bd11cd242f",
            "a8ff7bb87ff92a6ecceefdf8a6811e33",
            "5254bbdd6c192aec0dab4246f2c0c8ae",
            "28e5826458f04a9c233f404979f6151e",
            "c8d50578e07c8537916d26a8fc551795",
            "0c14ff88d5f697122d1e04d99255b19b",
            "e29d4a43e71a7b0324e882b7f6635958",
            "e0d47f14f0119b8ed1931091b350c589",
            "d9f5ff6ed42ab4a81ac20cbc0d6f86d3",
            "9246bc7a518d4aa5f54b7f12ba080ebd",
            "66f19193ddef6ff8b973f20fb033c81e",
            "30b1021016ff433dbf3f2b3fa89849a0"
        ]

        self.assertEqual(self.hash_chunks_1, hash_chunks_2)  # add assertion here

    def test_serialize_deserialize(self):
        buf = self.hash_chunks_1.serialize()
        hash_list_2 = deserialize_hash_chunk_list_from_stream(BufferStream(buf))
        self.assertEqual(self.hash_chunks_1, hash_list_2)


class ChunkIdListTestCase(unittest.TestCase):
    chunk_id_list = ChunkIdList()

    def test_serialize_deserialize(self):
        buf = self.chunk_id_list.serialize()
        chunk_id_list_2 = deserialize_chunk_id_list_from_stream(BufferStream(buf))
        self.assertEqual(self.chunk_id_list, chunk_id_list_2)


if __name__ == '__main__':
    unittest.main()
