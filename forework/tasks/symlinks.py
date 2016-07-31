from ..basetask import BaseTask


class SymLinks(BaseTask):

    MAGIC_PATTERN = '^symbolic link.*'

    def __init__(self, path, *args, **kwargs):
        BaseTask.__init__(path, *args, **kwargs)

    def run(self):
        self._result = 'No action for symlink: {s!r}'.format(s=self._path)
