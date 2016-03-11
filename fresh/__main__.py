import os
import sys
import argparse

from . import scheduler

if sys.version_info < (3, 5):
    print('Python 3.5+ is required')
    sys.exit(os.EX_SOFTWARE)


def parse_args(args=None):
    if args is None:
        args = sys.argv
    parser = argparse.ArgumentParser(name='fresh')
    return parser.parse_args(args)


def main():
    sched = scheduler.get()
    print(sched)


main()
