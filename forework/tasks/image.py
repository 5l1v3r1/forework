import imagemounter

from ..basetask import BaseTask
from .diskscanner import DiskScanner
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
        valid_volumes = []
        skipped_volumes = []
        for volume in volumes:
            if not volume.mountpoint:
                logger.warn(
                    'Skipping empty mount point for volume {v}: {m!r}'.format(
                        v=volume,
                        m=volume.mountpoint,
                        ))
                self.add_warning('Skipped volume {v}'.format(v=volume))
                skipped_volumes.append(volume)
                continue
            logger.info('Adding mount point {mp}'.format(mp=volume.mountpoint))
            self.add_next_task({
                'name': DiskScanner.__class__.__name__,
                'path': volume.mountpoint,
            })
            valid_volumes.append(volume)
        # NOTE do not unmount the volumes or the next tasks will fail
        self._result = 'Volumes: {vv} valid, {iv} skipped'.format(
            vv=len(valid_volumes),
            iv=len(skipped_volumes),
        )
