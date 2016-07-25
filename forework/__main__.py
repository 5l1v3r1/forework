import sys
import time
import argparse

import IPython

from . import scheduler
from . import utils, config
# the following imports are useful in the shell
from .basetask import BaseTask, find_tasks
from .tasks.raw import Raw


logger = utils.get_logger(__name__)

# populate global namespace with tasks
taskmap = {task.__name__: task for task in find_tasks()}
globals().update(taskmap)
del taskmap


def parse_args(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(prog='forework')
    parser.add_argument('-c', '--config', required=True,
                        help='Configuration file for the investigation (YAML)')
    return parser.parse_args(args)


def main():
    args = parse_args()
    conf = config.ForeworkConfig(args.config)
    sched = scheduler.get()
    sched.set_config(conf)
    IPython.embed()

main()
