import sys
from distutils.core import setup

import forework

if sys.version_info[:2] < forework.config.REQUIRED_PYTHON_VERSION:
    raise SystemExit('At least Python {} is required'.format(
        '.'.join(forework.config.REQUIRED_PYTHON_VERSION),
    ))


setup(
    name='ForeWork',
    version='0.1',
    author='Andrea Barberio',
    author_email='<insomniac@slackware.it>',
    description='Forensic Shell',
    url='https://github.com/insomniacslk/forework',
    packages=['forework'],
)
