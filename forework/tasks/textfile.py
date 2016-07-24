import re
import mmap

from ..basetask import BaseTask
from .. import utils


logger = utils.get_logger(__name__)


class TextFile(BaseTask):

    MAGIC_PATTERN = '^ASCII text.*'

    def __init__(self, path, conf, pattern=None, *args, **kwargs):
        self._path = path
        BaseTask.__init__(self, path, conf, *args, **kwargs)

    def run(self):
        try:
            grep = self._config.get(self.__class__.__name__)['grep']
        except KeyError:
            msg = 'No pattern requested for {path!r}'.format(
                path=self._path,
            )
            logger.info(msg)
            self._result = msg
            return

        # TODO handle regex flags in configuration
        pattern = re.compile(grep, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        # TODO implement grep for large text files. Can't mix mmap and text
        #      regex'es.
        with open(self._path) as fd:
            match = pattern.search(fd.read())
            msg = 'Pattern {pattern!r} {found}found in {path!r}{at}'.format(
                pattern=grep,
                found='' if match else 'not ',
                path=self._path,
                at='' if match is None else ' at {}'.format(match.span()),
            )
            logger.info(msg)
            self._result = msg
