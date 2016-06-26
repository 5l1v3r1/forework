from ..basetask import BaseTask


class DOSPartition(BaseTask):

    MAGIC_PATTERN = r'^DOS 3.0\+ 16-bit FAT \(up to 32M\)$'
