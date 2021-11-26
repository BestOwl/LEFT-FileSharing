# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su

import unittest

from left.left_packet import *
from left.stream import BufferStream, new_empty_buffer_stream


class MyTestCase(unittest.TestCase):
    def test_to_bytes(self):
        packet = LeftPacket(OPCODE_CONNECT)
        packet.target = b"LEFT"
        packet.version = b"\x10"
        packet.data = b"f"
        io_stream = new_empty_buffer_stream()
        packet.write_bytes(io_stream)
        self.assertEqual(b"\x80\x00\x00\x00\x0E\x46\x4C\x45\x46\x54\x76\x10" + HEADER_F0_END_OF_HEADERS + b"f",
                         io_stream.buffer)  # expected, actual

    def test_opcode_only_header(self):
        packet = LeftPacket(OPCODE_SUCCESS)
        buf_stream = new_empty_buffer_stream()
        packet.write_bytes(buf_stream)

        self.assertEqual(OPCODE_SUCCESS + b"\x00\x00\x00\x05", buf_stream.buffer)

        new_packet = read_packet_from_stream(buf_stream)
        self.assertEqual(OPCODE_SUCCESS, new_packet.opcode)

    def test_data_integrity(self):
        packet = LeftPacket(OPCODE_CONNECT)
        packet.target = b"TEST"
        packet.version = b"\xA0"
        packet.data = b"foobar"

        io_stream = new_empty_buffer_stream()
        packet.write_bytes(io_stream)
        remote_packet = read_packet_from_stream(io_stream)
        self.assertEqual(OPCODE_CONNECT, remote_packet.opcode)
        self.assertEqual(b"TEST", remote_packet.target)
        self.assertEqual(b"\xA0", remote_packet.version)
        self.assertEqual(b"foobar", remote_packet.data)

    def test_long_packet(self):
        data_buf = b'\xd0share/.1.txt.swp\x00\x16\xbb\x07\xd8r\xae\xf1\xb825facfae00c05ba9847448af41100a01\x00\xd0share/1.16.4/1.16.4.json\x00\x16\xbb\n\x98\x8cvp\xdf8b6907ce0b4771df0a870b0c9fc81817\x00\xd0share/1.16.4/forge-1.16.4-35.1.4.jar\x00\x16\xbb\n\x98\xa7*\x8f5fb74fa8090da23e20eaf34aee847d0b1\x00\xd0share/1.16.4/libraries/com/electronwill/night-config/core/3.6.2/core-3.6.2.jar\x00\x16\xbb\n\x98\xe6\xd3`\xb3243fc0b7f1e509aaca3550c14d8f60af\x00\xd0share/1.16.4/libraries/com/electronwill/night-config/toml/3.6.2/toml-3.6.2.jar\x00\x16\xbb\n\x98\xcfu\xc6#7b2339065e252b1c187d39351d84a09f\x00\xd0share/1.16.4/libraries/com/github/jponge/lzma-java/1.3/lzma-java-1.3.jar\x00\x16\xbb\n\x98\xd1\x9b\x1a\xdd839a86cf1533e75121d574317de78692\x00\xd0share/1.16.4/libraries/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar\x00\x16\xbb\n\x98\xe7\x10j\x1cdd83accb899363c32b07d7a1b2e4ce40\x00\xd0share/1.16.4/libraries/com/google/code/gson/gson/2.8.0/gson-2.8.0.jar\x00\x16\xbb\n\x98\xf3\xb3]\x0ca42f1f5bfa4e6f123ddcab3de7e0ff81\x00\xd0share/1.16.4/libraries/com/google/errorprone/error_prone_annotations/2.1.3/error_prone_annotations-2.1.3.jar\x00\x16\xbb\n\x98\xfa\xdawu97504b36cf871722d81a4b9e114f2a16\x00\xd0share/1.16.4/libraries/com/google/guava/guava/20.0/guava-20.0.jar\x00\x16\xbb\n\x98\xe8\xbb\xac\x01f32a8a2524620dbecc9f6bf6a20c293f\x00\xd0share/1.16.4/libraries/com/google/guava/guava/25.1-jre/guava-25.1-jre.jar\x00\x16\xbb\n\x98\xf5\xd8\xb1\xc5da3838847d109ac435f0d3ed4ae1c794\x00\xd0share/1.16.4/libraries/com/google/j2objc/j2objc-annotations/1.1/j2objc-annotations-1.1.jar\x00\x16\xbb\x0e\xfc\xa7\x057\xbf49ae3204bb0bb9b2ac77062641f4a6d7\x00\xd0share/1.16.4/libraries/com/nothome/javaxdelta/2.0.1/javaxdelta-2.0.1.jar\x00\x16\xbb\x0e\xfc\xaa[\xb7b02058f3edd701db5a5230a427b9e8979\x00\xd0share/1.16.4/libraries/commons-io/commons-io/2.4/commons-io-2.4.jar\x00\x16\xbb\x0e\xfc\xab\x8c\xe4\xf77f97854dc04c119d461fed14f5d8bb96\x00\xd0share/1.16.4/libraries/cpw/mods/grossjava9hacks/1.3.0/grossjava9hacks-1.3.0.jar\x00\x16\xbb\x0e\xfc\xaa\x1e\xaeDc5c05d52fcef5479e0ea069f30c6ceb5\x00\xd0share/1.16.4/libraries/cpw/mods/modlauncher/8.0.6/modlauncher-8.0.6.jar\x00\x16\xbb\x0e\xfc\xab\x8c\xe4\xf769afb8c6a9b2e6e0f1df0ee4069fa119\x00\xd0share/1.16.4/libraries/de/oceanlabs/mcp/mcp_config/1.16.4-20201102.104115/mcp_config-1.16.4-20201102.104115-mappings.txt\x00\x16\xbb\x0e\xfc\xac\xbe\x12\x8debaac697ed79436ebb0a7fb142b2633c\x00\xd0share/1.16.4/libraries/de/oceanlabs/mcp/mcp_config/1.16.4-20201102.104115/mcp_config-1.16.4-20201102.104115.zip\x00\x16\xbb\x0e\xfc\xab\x8c\xe4\xf78fe209c335c327a6ba8bca75f6e6d14c\x00\xd0share/1.16.4/libraries/de/siegmar/fastcsv/1.0.2/fastcsv-1.0.2.jar\x00\x16\xbb\x0e\xfc\xaa\x1e\xaeDd02c17f6c6744222ce05dc4b1c066b08\x00\xd0share/1.16.4/libraries/net/jodah/typetools/0.8.1/typetools-0.8.1.jar\x00\x16\xbb\x0e\xfc\xae\xe3d\x9b0eb481e955b455e61bd5ea8f520f6009\x00\xd0share/1.16.4/libraries/net/md-5/SpecialSource/1.8.5/SpecialSource-1.8.5.jar\x00\x16\xbb\x0e\xfc\xa8\xb0w\x90bfb833db1ebffacce294d325e1031cb9\x00\xd0share/1.16.4/libraries/net/minecraft/server/1.16.4-20201102.104115/server-1.16.4-20201102.104115-extra.jar\x00\x16\xbb\x0e\xfc\xe1n\xf1cb4cb9cb982960689472973abe3e4b485\x00\xd0share/1.16.4/libraries/net/minecraft/server/1.16.4-20201102.104115/server-1.16.4-20201102.104115-extra.jar.cache\x00\x16\xbb\x0e\xfc\xb5\xcdl\xfe88164aa8a4697214ce989e2f45afa7e7\x00\xd0share/1.16.4/libraries/net/minecraft/server/1.16.4-20201102.104115/server-1.16.4-20201102.104115-slim.jar\x00\x16\xbb\x0e\xfc\xbe\x9f\xbeR7ad11935b5c8310fa5f6fd9d86f5898d\x00\xd0share/1.16.4/libraries/net/minecraft/server/1.16.4-20201102.104115/server-1.16.4-20201102.104115-slim.jar.cache\x00\x16\xbb\x0e\xfc\xb8l\xd1Ga1739455f421115d1c9405245d797ef3\x00\xd0share/1.16.4/libraries/net/minecraft/server/1.16.4-20201102.104115/server-1.16.4-20201102.104115-srg.jar\x00\x16\xbb\x0e\xfc\xc0\r\xf5\x05793c35aaa5ff16fce8caed9c37cbab06\x00\xd0share/1.16.4/libraries/net/minecraftforge/accesstransformers/2.2.0-shadowed/accesstransformers-2.2.0-shadowed.jar\x00\x16\xbb\x0e\xfc\xba\x18\x11\x196ee328e0eda1765b17fb842135d3194b\x00\xd0share/1.16.4/libraries/net/minecraftforge/binarypatcher/1.0.12/binarypatcher-1.0.12.jar\x00\x16\xbb\x0e\xfc\xb7;\xa3\xb3838cc74c3c15daca8a30940dad489532\x00\xd0share/1.16.4/libraries/net/minecraftforge/coremods/3.0.0/coremods-3.0.0.jar\x00\x16\xbb\x0e\xfc\xb7;\xa3\xb39b0b4d1d8b5815d3f693ac82d4128f13\x00\xd0share/1.16.4/libraries/net/minecraftforge/eventbus/3.0.5-service/eventbus-3.0.5-service.jar\x00\x16\xbb\x0e\xfc\xba\xcf,se6f00d34a82bd71ca95af9dd02194997\x00\xd0share/1.16.4/libraries/net/minecraftforge/forge/1.16.4-35.1.4/forge-1.16.4-35.1.4-server.jar\x00\x16\xbb\x0e\xfc\xc2pP0594149de083aa3ed15cb196513a00d87\x00\xd0share/1.16.4/libraries/net/minecraftforge/forge/1.16.4-35.1.4/forge-1.16.4-35.1.4-universal.jar\x00\x16\xbb\x0e\xfc\xc3dt\xa810f23d3c8f59a5872fec0225f4dd9bbd\x00\xd0share/1.16.4/libraries/net/minecraftforge/forge/1.16.4-35.1.4/forge-1.16.4-35.1.4.jar\x00\x16\xbb\x0e\xfc\xc0\x88\x07Afb74fa8090da23e20eaf34aee847d0b1\x00\xd0share/1.16.4/libraries/net/minecraftforge/forgespi/3.2.0/forgespi-3.2.0.jar\x00\x16\xbb\x0e\xfc\xc1\xb94\xd68f1f6942d17d88d704324e8000666a1a\x00\xd0share/1.16.4/libraries/net/minecraftforge/installertools/1.1.11/installertools-1.1.11.jar\x00\x16\xbb\x0e\xfc\xc6\xba\xf4L98a5eabc02648dccc7dbbbd046ff7da9\x00\xd0share/1.16.4/libraries/net/minecraftforge/jarsplitter/1.1.2/jarsplitter-1.1.2.jar\x00\x16\xbb\x0e\xfc\xc6@\xe2\x106336b555885a01ec1b129a0e4074428f\x00\xd0share/1.16.4/libraries/net/minecraftforge/unsafe/0.2.0/unsafe-0.2.0.jar\x00\x16\xbb\x0e\xfc\xc4\x1b\x90\x032d1016ebe4c1a63dd50a59d26bd12db1\x00\xd0share/1.16.4/libraries/net/minecrell/terminalconsoleappender/1.2.0/terminalconsoleappender-1.2.0.jar\x00\x16\xbb\x0e\xfc\xd0\xbes5679363fa893293791e55a21f81342f87\x00\xd0share/1.16.4/libraries/net/sf/jopt-simple/jopt-simple/4.9/jopt-simple-4.9.jar\x00\x16\xbb\x0e\xfc\xcf\x133b39c6476e4de3d4f90ad4ca0ddca48ec2\x00\xd0share/1.16.4/libraries/net/sf/jopt-simple/jopt-simple/5.0.4/jopt-simple-5.0.4.jar\x00\x16\xbb\x0e\xfc\xd2i\xb3\x06eb0d9dffe9b0eddead68fe678be76c49\x00\xd0share/1.16.4/libraries/net/sf/opencsv/opencsv/2.3/opencsv-2.3.jar\x00\x16\xbb\x0e\xfc\xd1\xb2\x97\xac9eebabaa007dc329845e5ab3c12b4e6b\x00\xd0share/1.16.4/libraries/org/apache/logging/log4j/log4j-api/2.11.2/log4j-api-2.11.2.jar\x00\x16\xbb\x0e\xfc\xd4\xcc\x0e13f7ee51e3dd0830de799dae0b90243dd\x00\xd0share/1.16.4/libraries/org/apache/logging/log4j/log4j-core/2.11.2/log4j-core-2.11.2.jar\x00\x16\xbb\x0e\xfc\xd7\xe5\x84\xb6c8bd8b5c5aaaa07a3dcbf57de01c9266\x00\xd0share/1.16.4/libraries/org/apache/maven/maven-artifact/3.6.0/maven-artifact-3.6.0.jar\x00\x16\xbb\x0e\xfc\xd6:D\xe489e95013b11f347e48c0525965600404\x00\xd0share/1.16.4/libraries/org/checkerframework/checker-qual/2.0.0/checker-qual-2.0.0.jar\x00\x16\xbb\x0e\xfc\xd6:D\xe494fe1af76c10006fbc5b988180b71bf0\x00\xd0share/1.16.4/libraries/org/codehaus/mojo/animal-sniffer-annotations/1.14/animal-sniffer-annotations-1.14.jar\x00\x16\xbb\x0e\xfc\xda\xc1\xf2\x1d9d42e46845c874f1710a9f6a741f6c14\x00\xd0share/1.16.4/libraries/org/jline/jline/3.12.1/jline-3.12.1.jar\x00\x16\xbb\x0e\xfd\x02U\xdb\x85ffd8c9d6eb8a8456ef505c8ef9fc777d\x00\xd0share/1.16.4/libraries/org/ow2/asm/asm/6.1.1/asm-6.1.1.jar\x00\x16\xbb\x0e\xfd\x1b!\x8f\xad04b72e489b64c54d5776ab59f330bd23\x00\xd0share/1.16.4/libraries/org/ow2/asm/asm/7.2/asm-7.2.jar\x00\x16\xbb\x0e\xfd\t\xb9\xf6%26cf10dfd4729fd22fcae0694e041167\x00\xd0share/1.16.4/libraries/org/ow2/asm/asm-analysis/6.1.1/asm-analysis-6.1.1.jar\x00\x16\xbb\x0e\xfd&\x193\x0eb58c31c1ca0496e6773cc0311f97ceda\x00\xd0share/1.16.4/libraries/org/ow2/asm/asm-analysis/7.2/asm-analysis-7.2.jar\x00\x16\xbb\x0e\xfd;\x14UXe0aa4ec0cfa837415818aac762ed5dc2\x00\xd0share/1.16.4/libraries/org/ow2/asm/asm-commons/6.1.1/asm-commons-6.1.1.jar\x00\x16\xbb\x0e\xfd1M\xdf\x8dca6299118bc7b85201671502526bd68b\x00\xd0share/1.16.4/libraries/org/ow2/asm/asm-commons/7.2/asm-commons-7.2.jar\x00\x16\xbb\x0e\xfd>-\xcb\xdd321121317a6c6221cc26e8f9ee97022f\x00\xd0share/1.16.4/libraries/org/ow2/asm/asm-tree/6.1.1/asm-tree-6.1.1.jar\x00\x16\xbb\x0e\xfd;\x14UXd640f7d0efc57192870f73a87f576469\x00\xd0share/1.16.4/libraries/org/ow2/asm/asm-tree/7.2/asm-tree-7.2.jar\x00\x16\xbb\x0e\xfd=9\xa7ec7214695c379f25861500e576a1f8cea\x00\xd0share/1.16.4/libraries/org/ow2/asm/asm-util/7.2/asm-util-7.2.jar\x00\x16\xbb\x0e\xfdET\xdd_0891d2562ab1db2a1d5fc013af9b40c5\x00\xd0share/1.16.4/libraries/org/spongepowered/mixin/0.8.2/mixin-0.8.2.jar\x00\x16\xbb\x0e\xfdY\xd5\xedm1f0c4faa50360623e49b9c2522edc602\x00\xd0share/1.16.4/libraries/trove/trove/1.0.2/trove-1.0.2.jar\x00\x16\xbb\x0e\xfd`\x08\xdav487d72e3da5947890376ddfc5e14442e\x00\xd0share/1.16.4/minecraft_server.1.16.4.jar\x00\x16\xbb\x0e\xfd\xc1Ob)c43dc4c1bda4f485428fc60d5b998270\x00\xd0share/1.txt\x00\x16\xbb\x0f\x13\x8a\xea\x83\x0b6721319c95c1f3a42367aaf372501c6b\x00'
        print(f"data buf len: {len(data_buf)}")
        packet = LeftPacket(OPCODE_SYNC_FILE_TABLE)
        packet.data = data_buf

        io_stream = new_empty_buffer_stream()
        packet.write_bytes(io_stream)

        remote_packet = read_packet_from_stream(io_stream)
        self.assertEqual(data_buf, remote_packet.data)


if __name__ == '__main__':
    unittest.main()
