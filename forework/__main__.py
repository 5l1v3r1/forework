import sys
import time
import argparse

from . import scheduler
from . import utils
from .tasks.fibonacci import Fibonacci
from .tasks.raw import Raw


logger = utils.get_logger(__name__)


def parse_args(args=None):
    if args is None:
        args = sys.argv
    parser = argparse.ArgumentParser(name='forework')
    return parser.parse_args(args)


def parallel_fibonacci():
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
    try:
        analyze_raw_file(sys.argv[1])
    except IndexError:
        print('Usage: {} <file>'.format(sys.argv[0]))
        sys.exit(1)

main()
