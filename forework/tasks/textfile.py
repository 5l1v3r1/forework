import re
import mmap

from ..basetask import BaseTask
from .. import utils


logger = utils.get_logger(__name__)


class TextFile(BaseTask):

    MAGIC_PATTERN = '^ASCII text.*'

    def __init__(self, path, pattern=None, *args, **kwargs):
        self._path = path
        self._pattern = pattern
        BaseTask.__init__(self, path, *args, **kwargs)

    def run(self):
        if self._pattern is None:
            msg = 'No pattern requested for {path!r}'.format(
                path=self._path,
            )
            logger.info(msg)
            self._result = msg
            return

        pattern = re.compile(self._pattern)
        with open(self._path) as fd:
            mm = mmap.mmap(fd.fileno(), 0)
            match = pattern.match(mm)
            msg = 'Pattern {pattern!r} {found}found in {path!r}'.format(
                pattern=self._pattern,
                found='' if match else 'not ',
                path=self._path,
            )
            logger.info(msg)
            self._result = msg
