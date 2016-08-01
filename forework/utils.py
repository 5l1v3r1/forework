import os
import time
import logging

import magic

from . import config


mage = magic.Magic()


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)

    formatter = logging.Formatter(
        '%(levelname)s|%(asctime)s|%(name)s|'
        '%(filename)s:%(lineno)s in %(funcName)s|%(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S%z'
    )
    formatter.converter = time.gmtime

    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.loglevel_console)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(config.logfile)
    file_handler.setLevel(config.loglevel_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_file_type(path):
    if os.path.isdir(path):
        return 'directory'
    if os.path.islink(path):
        return 'symbolic link'
    return mage.from_file(path)
