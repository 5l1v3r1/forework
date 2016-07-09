import os

import imagemounter

from ..basetask import BaseTask, find_tasks_by_filetype
from .. import utils


logger = utils.get_logger(__name__)


class Image(BaseTask):
    '''
    Task to handle MBR objects
    '''

    MAGIC_PATTERN = '^DOS/MBR boot sector.*'

    def run(self):
        logger.info('Parsing image {p}, ignoring offset'.format(p=self._path))
        image = imagemounter.ImageParser([self._path])
        volumes = list(image.init())
        for volume in volumes:
            if not volume.mountpoint:
                logger.warn('Skipping empty mount point for volume {v}'.format(
                    v=volume,
                ))
                continue
            logger.warn(os.listdir(volume.mountpoint))
            # TODO go through artifacts under volume.mountpoint
            # TODO carve
            # TODO yield tasks asynchronously
            pass
        image.clean()
        self._result = ''
