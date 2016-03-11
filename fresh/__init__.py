import os
import sys

if sys.version_info < (3, 5):
    print('Python 3.5+ is required, exiting.')
    sys.exit(os.EX_SOFTWARE)
