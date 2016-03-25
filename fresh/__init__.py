import os
import sys

from . import config


if sys.version_info < config.REQUIRED_PYTHON_VERSION:
    print('Python {}.{}+ is required, exiting.'.format(
        *config.REQUIRED_PYTHON_VERSION))
    sys.exit(os.EX_SOFTWARE)
