import sys

from distutils.core import setup


if sys.version_info[:2] < (3, 5):
    raise SystemExit('At least Python 3.5 is required')


setup(
    name='Fresh',
    version='0.1',
    author='Andrea Barberio',
    author_email='<insomniac@slackware.it>',
    description='Forensic Shell',
    url='https://github.com/insomniacslk/fresh',
    packages=['fresh'],
)
