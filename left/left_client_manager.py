# This file is part of Large Efficient Flexible and Trusty (LEFT) File Sharing
# Author: Hao Su <hao.su19@student.xjtlu.edu.cn>
# Copyright (c) 2021 Hao Su
import socket
import threading

from file_table import FileTable
from left_client import LeftClient


class LeftClientManager:

    def __init__(self, file_table: FileTable, left_server_port: int = 25560):
        self.file_table = file_table
        self.left_server_port = left_server_port
        self.clients = {}
        self.lock = threading.Lock()

    def try_connect(self, address: str):
        """
        Try to connect to peer's LeftServer
        :raise LeftError if unable to connect to peer
        """
        client = LeftClient(address, self.left_server_port, self.file_table)
        cmi = ClientManagementInfo(address, client)
        self.clients[address] = cmi
        try:
            client.connect()
            cmi.connecting.set()
        except socket.error:
            client.dispose()
            cmi.connecting.set()
            del self.clients[address]
            raise

    def is_connected(self, address: str):
        self.lock.acquire()
        cmi = None
        if address in self.clients:
            cmi = self.clients[address]
        self.lock.release()

        if cmi is not None:
            cmi.connecting.wait()
            return cmi.address in self.clients
        else:
            return False


class ClientManagementInfo:

    def __init__(self, address: str, client: LeftClient):
        self.address = address
        self.client = client
        self.connecting = threading.Event()
