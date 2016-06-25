from ..basetask import BaseTask, find_tasks_by_filetype

import magic


class Raw(BaseTask):
    '''
    Generic class to handle raw files and recognize them. It can be used as a
    starting point to analyze unknown artifacts. Requires filemagic .
    '''

    MAGIC_PATTERN = '.*'

    def __init__(self, path, *args, **kwargs):
        BaseTask.__init__(self, path, *args, **kwargs)

    def run(self):
        with magic.Magic() as mage:
            # Try to recognize the file content using libmagic
            filetype = mage.id_filename(self._path)
            # look for known handlers for this mime type
            # TODO search all the registered plugins
            # TODO if a plugin is found, enqueue/notify a new task
            # TODO if no plugin is found, leave without analysis
            self._result = filetype
            self.add_next_task({
                'name': find_tasks_by_filetype(filetype),
                'path': self._path
            })
