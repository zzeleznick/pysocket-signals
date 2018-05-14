from __future__ import print_function

import sys


def log(msg, *args):
    """Prints to stderr"""
    print(msg, *args, file=sys.stderr)

