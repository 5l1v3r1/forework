import sys
from distutils.core import setup

import fresh

if sys.version_info[:2] < fresh.config.REQUIRED_PYTHON_VERSION:
    raise SystemExit('At least Python {} is required'.format(
        '.'.join(fresh.config.REQUIRED_PYTHON_VERSION),
    ))


setup(
    name='Fresh',
    version='0.1',
    author='Andrea Barberio',
    author_email='<insomniac@slackware.it>',
    description='Forensic Shell',
    url='https://github.com/insomniacslk/fresh',
    packages=['fresh'],
)
