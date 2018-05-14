import time
import threading

from utils import log

class Player(object):

    def __init__(self):
        self._listening = False
        self.thread = threading.Thread(target=self.tick_tock)
        self.thread.daemon = True
        self.tock = threading.Event()

    def start(self):
        self._listening = True
        self.thread.start()

    def tick_tock(self, interval=3):
        log('Start of clock')
        while self._listening:
            sound = "tock" if self.tock.is_set() else "tick"
            log(sound)
            time.sleep(interval)
        log('End of clock')

    def toggle(self):
        if self.tock.is_set():
            self.tock.clear()
        else:
            self.tock.set()
