from __future__ import print_function

import sys
from functools import wraps

def log(msg, *args):
    """Prints to stderr"""
    print(msg, *args, file=sys.stderr)

def catch_error(fn):
    @wraps(fn)
    def caller(*args, **kws):
        try:
            return fn(*args, **kws)
        except Exception as e:
            log("{} failed:".format(fn.__name__), e)
    return caller
