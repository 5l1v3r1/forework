import os

from ..basetask import BaseTask, find_tasks_by_filetype
from .. import utils

import magic


logger = utils.get_logger(__name__)


class DirectoryScanner(BaseTask):

    MAGIC_PATTERN = 'directory'

    def __init__(self, path, *args, **kwargs):
        BaseTask.__init__(self, path, args, kwargs)

    def run(self):
        logger.info('Scanning directory point {mp}'.format(mp=self._path))
        mage = magic.Magic()
        for dirent in os.listdir(self._path):
            path = os.path.join(self._path, dirent)
            filetype = mage.from_file(path)
            tasknames = find_tasks_by_filetype(filetype)
            if len(tasknames) < 1:
                msg = 'Cannot find a task for {fn}'.format(fn=path)
                self.add_warning(msg)
                continue
            self.add_next_task({
                'name': tasknames[0],
                'path': path,
            })
        self._result = 'Found {tn} tasks, and {uf} unknown file types'.format(
            tn=len(self._next_tasks),
            uf=len(self._warnings),
        )
