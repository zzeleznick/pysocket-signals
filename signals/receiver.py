from __future__ import absolute_import

import atexit
import os
import signal

from utils import log
from player import Player

def on_exit():
    log('Exiting')

def on_interrupt(sig, frame):
    log('Interrupted')

def on_signal(sig, frame):
    log('Signal received', sig)

def on_interrupt(sig, frame):
    log('Interrupted')

def clock_toggler():
    player = Player()
    def handle_signal(sig, frame):
        log('Toggling')
        player.toggle()
    player.start()
    return handle_signal

def register():
    log('Registering signals')
    signal.signal(signal.SIGINT, on_interrupt)
    atexit.register(on_exit)
    examples = [signal.SIGALRM, signal.SIGINFO,
                signal.SIGUSR1, signal.SIGUSR2]
    for sig in examples:
        log('Registering', sig)
        signal.signal(sig, on_signal)
    signal.signal(signal.SIGURG, clock_toggler())


def main():
    pid = os.getpid()
    log('Running with pid', pid)
    register()

    while 1:
        pass

# signal.alarm
# signal.pause

if __name__ == '__main__':
    main()