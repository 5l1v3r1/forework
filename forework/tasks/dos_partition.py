from ..basetask import BaseTask


class DOSPartition(BaseTask):

    # TODO also add the pattern returned by libmagic
    MAGIC_PATTERN = r'^DOS 3.0\+ 16-bit FAT \(up to 32M\)$'

    def run(self):
        with open(self._path, 'rb') as fd:
            fd.seek(self._offset)
