from ..basetask import BaseTask

import magic


class Raw(BaseTask):
    '''
    Generic class to handle raw files and recognize them. It can be used as a
    starting point to analyze unknown artifacts. Requires filemagic .
    '''

    MAGIC_PATTERN = '.*'

    def __init__(self, path, *args, **kwargs):
        self._path = path
        BaseTask.__init__(self, *args, **kwargs)

    def run(self):
        with magic.Magic() as mage:
            # Try to recognize the file content using libmagic
            mimetype = mage.id_filename(self._path)
            # look for known handlers for this mime type
            # TODO search all the registered plugins
            # TODO if a plugin is found, enqueue/notify a new task
            # TODO if no plugin is found, leave without analysis
            self._result = mimetype
