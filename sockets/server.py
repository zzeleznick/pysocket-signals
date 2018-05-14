import socket
from os.path import abspath, dirname, join

from utils import log, catch_error
from sockets.base import Socket

class SocketServer(Socket):

    def __init__(self, name=""):
        super(SocketServer, self).__init__(name)
        self._remove_socket_file()
        log("=== Opening socket ===")
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.socket_file)
        self.connection = None
        self._listening = False

    def listen(self):
        log("=== Listening ===")
        self.server.listen(1)
        log("=== Waiting for a Connection ===")
        self.connection, _ = self.server.accept()
        log('*** Accepted connection ***')
        self._listening = True

    def read(self):
        if not self._listening:
            self.listen()
        log("=== Waiting for input === ")
        msg = self.connection.recv(1024)
        log('Received', msg or self.EMPTY_MESSAGE)
        return msg

    @catch_error
    def write(self, res):
        self.connection.send("{}".format(res))

    def start(self, restart=True):
        while True:
            if self.read():
                continue
            # Empty response
            if not restart:
                break
            # Reset otherwise
            self.reset()
        log('read_loop completed')

    def close(self):
        log("=== Cleaning up the connection ===")
        self._listening = False
        if self.connection:
            self.connection.close()

    def reset(self):
        self.close()
        self.listen()

    def tearDown(self):
        self.close()
        self.server.close()

