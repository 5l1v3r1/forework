import subprocess

from ..basetask import BaseTask
from .. import utils


logger = utils.get_logger(__name__)


class DiskScanner(BaseTask):

    MAGIC_PATTERN = 'directory'

    def __init__(self, path, *args, **kwargs):
        BaseTask.__init__(self, path, args, kwargs)

    def run(self):
        logger.info('Scanning mount point {mp}'.format(mp=self._path))
        # do stuff
        subprocess.call(['umount', self._path])
