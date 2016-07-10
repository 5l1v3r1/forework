import os
import logging

REQUIRED_PYTHON_VERSION = (3, 4)
# If true, tasks are cached - all subsequent calls to `basetask.find_tasks` will
# use cached results, and will not discover newly added plugins unless restarted
ENABLE_TASKS_CACHE = True

src_dir = os.path.dirname(__file__)
tasks_dir = os.path.join(src_dir, 'tasks')
logfile = './forework.log'
loglevel_console = logging.WARNING
loglevel_file = logging.DEBUG
