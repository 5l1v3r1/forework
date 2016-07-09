from ..basetask import BaseTask, find_tasks_by_filetype

import magic


class Raw(BaseTask):
    '''
    Generic class to handle raw files and recognize them. It can be used as a
    starting point to analyze unknown artifacts. Requires filemagic .
    '''

    # This is a special task, and the MAGIC_PATTERN is actually ignored
    MAGIC_PATTERN = '.*'

    def run(self):
        self.logger.info('Trying to identify {p} at offset {o}'.format(
            p=self._path,
            o=self._offset,
        ))
        mage = magic.Magic()
        # Try to recognize the file content using libmagic
        filetype = mage.from_file(self._path)
        self._result = filetype
        self.add_next_task({
            'name': find_tasks_by_filetype(filetype),
            'path': self._path
        })
        self.logger.info('File {p} (offset {o}) identified as {t}'.format(
            p=self._path,
            o=self._offset,
            t=self._result,
        ))
