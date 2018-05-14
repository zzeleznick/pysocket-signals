import socket
import threading
from thread import interrupt_main

from utils import log, catch_error
from sockets.base import Socket

class SocketClient(Socket):

    def __init__(self, name=""):
        super(SocketClient, self).__init__(name)
        self.client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.reader_thread = None
        self._listening = False

    def connect(self):
        self.client.connect(self.socket_file)
        self._listening = True

    def read(self):
        log('Waiting for input')
        msg = self.client.recv(1024)
        log('** Received', msg, '**')
        return msg

    @catch_error
    def write(self, res):
        self.client.send("{}".format(res))

    def start(self):
        log('Starting reader_thread')
        if not self._listening:
            self.connect()
        self.reader_thread = threading.Thread(target=self.read_loop)
        self.reader_thread.daemon = True
        self.reader_thread.start()

    def read_loop(self):
        while self._listening:
            if not self.read():
                log(self.EMPTY_MESSAGE)
                break
        log('read_loop completed -- server exited?')
        interrupt_main()

    def close(self):
        self._listening = False
        if self.reader_thread:
            self.reader_thread.join(1)
        if self.client:
            self.client.close()

    def tearDown(self):
        self.close()
