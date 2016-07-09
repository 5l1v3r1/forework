from ..basetask import BaseTask
from .. import utils


logger = utils.get_logger(__name__)


class DOSPartition(BaseTask):

    # TODO also add the pattern returned by libmagic
    MAGIC_PATTERN = r'^DOS 3.0\+ 16-bit FAT \(up to 32M\)$'

    def run(self):
        logger.debug('Opening {fn} at offset {off}'.format(
            fn=self._path,
            off=self._offset,
        ))
        # TODO implement
        self._result = ''
