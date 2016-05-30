import os
import logging

REQUIRED_PYTHON_VERSION = (3, 4)

src_dir = os.path.dirname(__file__)
tasks_dir = os.path.join(src_dir, 'tasks')
logfile = './forework.log'
loglevel_console = logging.INFO
loglevel_file = logging.DEBUG
