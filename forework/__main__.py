import sys
import time
import argparse

import IPython

from . import scheduler
from . import utils, config
from .basetask import BaseTask
from .tasks.raw import Raw
from .tasks.image import Image


logger = utils.get_logger(__name__)


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
