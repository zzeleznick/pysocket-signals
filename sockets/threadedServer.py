import argparse
import socket
import threading
import time
from itertools import count
from collections import OrderedDict
from os.path import abspath, dirname, join

from utils import log, catch_error
from sockets.base import Socket


class ThreadedSocketServer(Socket):
    ECHO_PATTERN = "echo"

    def __init__(self, name=""):
        super(ThreadedSocketServer, self).__init__(name)
        self._remove_socket_file()
        log("=== Opening socket ===")
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.socket_file)
        self.connections = OrderedDict()
        self.threads = OrderedDict()
        self.counter = count(1)
        self._listening = False

    @catch_error
    def write(self, connection, res):
        connection.send("{}".format(res))

    def read(self, connection, conn_idx=1):
        """A threaded read"""
        while self._listening:
            log("=== Thread-{} Waiting for input === ".format(conn_idx))
            msg = connection.recv(1024)
            log('** Thread-{} Received {} **'.format(conn_idx, msg or self.EMPTY_MESSAGE))
            if not msg:
                log('** Thread-{} Closing due to empty message **'.format(conn_idx))
                break
            self.process_message(msg, connection, conn_idx)
        # End of listen
        self.close_connection(conn_idx)
        self.release_reader_thread(conn_idx)
        log("** Thread-{} exits **".format(conn_idx))

    def release_reader_thread(self, conn_idx):
        if conn_idx in self.threads:
            # Cannot join current thread (https://github.com/python/cpython/blob/2.7/Lib/threading.py#L931)
            # Just remove reference to it
            log("** Releasing thread {} **".format(conn_idx))
            del self.threads[conn_idx]

    def close_connection(self, conn_idx):
        if conn_idx in self.connections:
            log("** Closing connection {} **".format(conn_idx))
            self.connections[conn_idx].close()
            del self.connections[conn_idx]

    def process_message(self, msg, connection, conn_idx):
        if msg.startswith(self.ECHO_PATTERN):
            msg = msg.lstrip(self.ECHO_PATTERN).strip()
            log('** Thread-{} Writing back message {} **'.format(conn_idx, msg))
            self.write(connection, msg)

    @catch_error
    def accept_connection(self):
        self.server.listen(1)
        log("=== Waiting for a Connection ===")
        connection, _ = self.server.accept()
        conn_idx = next(self.counter)
        log('*** Accepted connection {} ***'.format(conn_idx))
        self.connections[conn_idx] = connection
        thread = threading.Thread(target=self.read, args=(connection, conn_idx,))
        self.threads[conn_idx] = thread
        thread.daemon = True
        thread.start()

    def listen_for_connections(self):
        log("=== Listening ===")
        self._listening = True
        while self._listening:
            self.accept_connection()
        self._listening = False
        log("=== End of listen_for_connections ===")

    def start(self):
        self.listen_for_connections()

    def close(self):
        log("=== Cleaning up the connections: {} ===".format(self.connections))
        for (idx, connection) in self.connections.iteritems():
            log("** Closing connecton {} **".format(idx))
            connection.close()
        for (idx, thread) in self.threads.iteritems():
            thread.join(1)
        log("=== Finished close ===")

    def tearDown(self):
        self.close()
        self._remove_socket_file()
