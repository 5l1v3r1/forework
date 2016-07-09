import sys
import time
import argparse

import IPython

from . import scheduler
from . import utils
from .basetask import BaseTask
from .tasks.raw import Raw
from .tasks.image import Image


logger = utils.get_logger(__name__)


def parse_args(args=None):
    if args is None:
        args = sys.argv
    parser = argparse.ArgumentParser(name='forework')
    return parser.parse_args(args)


def analyze_raw_file(filename):
    print('Analyzing {}'.format(filename))
    sched = scheduler.get()
    task = Raw(filename)
    sched.enqueue(task)
    sched.start()
    TIMEOUT = 10
    logger.debug('Scheduler will run for {t} seconds'.format(t=TIMEOUT))
    time.sleep(TIMEOUT)
    logger.info('Stopping scheduler after {t} seconds'.format(t=TIMEOUT))
    sched.stop()


def main():
    sched = scheduler.get()
    IPython.embed()

main()
