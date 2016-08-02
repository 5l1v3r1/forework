import zipfile
import tempfile

from ..basetask import BaseTask
from .directoryscanner import DirectoryScanner
from .. import utils


logger = utils.get_logger(__name__)


class ZipFile(BaseTask):

    MAGIC_PATTERN = '^Zip archive data.*'

    def __init__(self, path, *args, **kwargs):
        BaseTask.__init__(self, path, *args, **kwargs)

    def run(self):
        outdir = self.conf.get('outdir', tempfile.mkdtemp())
        with zipfile.ZipFile(self._path) as zf:
            zf.extractall(outdir)
        msg = 'Zip file {z!r} extracted at {t!r}'.format(
            z=self._path,
            t=outdir,
        )
        logger.info(msg)
        self.add_next_task({
            'name': DirectoryScanner.__name__,
            'path': outdir,
        })
        self._result = msg
