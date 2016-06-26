import time
import logging

from . import config


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

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
