from ..basetask import BaseTask


class MBR(BaseTask):
    '''
    Task to handle MBR objects
    '''

    MAGIC_PATTERN = '^DOS/MBR boot sector;.+'

    def __init__(self, path, *args, **kwargs):
        BaseTask.__init__(self, path, *args, **kwargs)

    def run(self):
        pass
