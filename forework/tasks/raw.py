from ..basetask import BaseTask, find_tasks_by_filetype
from .. import utils


logger = utils.get_logger(__name__)


class Raw(BaseTask):
    '''
    Generic class to handle raw files and recognize them. It can be used as a
    starting point to analyze unknown artifacts. Requires filemagic .
    '''

    # This is a special task, and the MAGIC_PATTERN is actually ignored
    MAGIC_PATTERN = '.*'

    def __init__(self, path, *args, **kwargs):
        BaseTask.__init__(self, path, *args, **kwargs)

    def run(self):
        logger.info('Trying to identify {p} at offset {o}'.format(
            p=self._path,
            o=self._offset,
        ))
        # Try to recognize the file content using libmagic
        filetype = utils.get_file_type(self._path)
        self.add_next_task({
            'name': find_tasks_by_filetype(filetype),
            'path': self._path
        })
        logger.info('File {p} (offset {o}) identified as {t}'.format(
            p=self._path,
            o=self._offset,
            t=self._result,
        ))
        self._result = filetype
