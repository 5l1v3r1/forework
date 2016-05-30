import sys
import time
import argparse

from . import scheduler
from . import utils
from .tasks.fibonacci import Fibonacci


logger = utils.get_logger(__name__)


def parse_args(args=None):
    if args is None:
        args = sys.argv
    parser = argparse.ArgumentParser(name='forework')
    return parser.parse_args(args)


def main():
    sched = scheduler.get()
    tasks = [Fibonacci(n) for n in range(100)]
    logger.info('Created scheduler: {s}'.format(s=sched))
    sched.enqueue_many(tasks)
    sched.start()
    TIMEOUT = 10
    logger.debug('Scheduler will run for {t} seconds'.format(t=TIMEOUT))
    time.sleep(TIMEOUT)
    logger.info('Stopping scheduler after {t} seconds'.format(t=TIMEOUT))
    sched.stop()


main()
