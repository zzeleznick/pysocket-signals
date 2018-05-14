import atexit
import os
import signal
from abc import ABCMeta, abstractmethod
from os.path import abspath, dirname, join, exists


from utils import log

class Socket(object):
    __metaclass__ = ABCMeta
    DEFAULT_NAME = join(abspath(dirname(__file__)), 'test.socket')
    EMPTY_MESSAGE = '[empty message]'

    def __init__(self, name=""):
        self.socket_file = name or self.DEFAULT_NAME
        signal.signal(signal.SIGINT, self.sig_handler)
        atexit.register(self.tearDown)

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def tearDown(self):
        pass

    def _remove_socket_file(self):
        if exists(self.socket_file):
            os.remove(self.socket_file)

    def sig_handler(self, sig, frame):
        log("** SIGINT Received **")
        self.tearDown()
        raise KeyboardInterrupt()
