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
        # listdir can be put in trouble with directories with a large number of
        # files.
        # TODO use a proper streaming scheduler and yield the files while they
        # are found
        for dirent in os.listdir(self._path):
            path = os.path.join(self._path, dirent)
            if os.path.isdir(path):
                filetype = 'directory'
            else:
                filetype = mage.from_file(path)
            tasknames = find_tasks_by_filetype(filetype)
            if len(tasknames) < 1:
                msg = 'Cannot find a task for {fn}'.format(fn=path)
                self.add_warning(msg)
                continue
            self.add_next_task({
                'name': tasknames,
                'path': path,
            })
        self._result = 'Found {tn} tasks, and {uf} unknown file types'.format(
            tn=len(self._next_tasks),
            uf=len(self._warnings),
        )
