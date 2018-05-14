import socket
import threading
import time
from collections import OrderedDict
from itertools import count
from os.path import abspath, dirname, join
from Queue import Queue

from utils import log, catch_error
from sockets.threadedServer import ThreadedSocketServer

class ThreadedSocketServerCombo(ThreadedSocketServer):
    TASK_PATTERN = "task"

    def __init__(self, name=""):
        super(ThreadedSocketServerCombo, self).__init__(name)
        self.queue = Queue()

    def read(self, connection, conn_idx=None):
        """A threaded read"""
        task_ctr = count(1)  # counter for the current thread
        while self._listening:
            log("=== Thread-{} Waiting for input === ".format(conn_idx))
            msg = connection.recv(1024)
            log('** Thread-{} Received {} **'.format(conn_idx, msg or self.EMPTY_MESSAGE))
            if not msg:
                log('** Thread-{} Closing due to empty message **'.format(conn_idx))
                break
            self.process_message(msg, connection, conn_idx, task_ctr)
        # End of listen
        self.close_connection(conn_idx)
        self.release_reader_thread(conn_idx)
        log("** Thread-{} exits **".format(conn_idx))

    def process_message(self, msg, connection, conn_idx, task_ctr):
        if msg.startswith(self.ECHO_PATTERN):
            res = msg.lstrip(self.ECHO_PATTERN).strip()
            log('** Thread-{} Writing back response {} **'.format(conn_idx, res))
            self.write(connection, res)
        elif msg.startswith(self.TASK_PATTERN):
            task = msg.lstrip(self.ECHO_PATTERN).strip()
            task_id = "{}-{}".format(conn_idx, next(task_ctr))
            res = "Added task ({}): '{}' - Qsize: {}".format(task_id, task, self.queue.qsize())
            log('** Thread-{} {} **'.format(conn_idx, res))
            self.queue.put((task_id, task))
            self.write(connection, res)

    def do_work(self):
        log("=== Starting process_queue ===")
        self._listening = True
        while self._listening:
            task_id, task = self.queue.get()
            log('** Executing task ({}): "{}" **'.format(task_id, task))
            time.sleep(3) # add fake delay
            self.queue.task_done()
            conn_idx = int(task_id.split("-")[0])
            res = "Completed task ({}): '{}'".format(task_id, task)
            if conn_idx in self.connections:
                connection = self.connections[conn_idx]
                self.write(connection, res)
            else:
                # Possibly client disconnected while we were working
                log("Could not send client {} done status".format(conn_idx))

        log("=== End of process_queue ===")

    def do_work_async(self):
        thread = threading.Thread(target=self.do_work)
        thread.daemon = True
        thread.start()

    def start(self):
        self.do_work_async()
        self.listen_for_connections()
