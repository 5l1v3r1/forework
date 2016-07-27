import imagemounter

from ..basetask import BaseTask, find_tasks_by_filetype
from .. import utils


logger = utils.get_logger(__name__)


class Image(BaseTask):
    '''
    Task to handle MBR objects
    '''

    MAGIC_PATTERN = (
        '^DOS/MBR boot sector.*|'
        '^EWF/Expert Witness/EnCase image file format$'
    )

    def run(self):
        logger.info('Parsing image {p}, ignoring offset'.format(p=self._path))
        image = imagemounter.ImageParser([self._path])
        try:
            volumes = list(image.init(swallow_exceptions=False))
        except Exception as exc:
            logger.exception(exc)
            raise

        valid_volumes = []
        skipped_volumes = []
        for volume in volumes:
            logger.info('Volume found: {v}'.format(v=str(volume)))
#            if 'statfstype' in volume.info and not volume.is_mounted:
#                volume.mount()
            if not volume.mountpoint:
                logger.warn(
                    'Skipping empty mount point for volume {v}: {m!r}. '
                    'Non-mountable partition or insufficient permissions'.format(
                        v=volume,
                        m=volume.mountpoint,
                        ))
                self.add_warning('Skipped volume {v}'.format(v=volume))
                skipped_volumes.append(volume)
                continue
            logger.info('Adding mount point {mp}'.format(mp=volume.mountpoint))
            self.add_next_task({
                'name': find_tasks_by_filetype('directory'),
                'path': volume.mountpoint,
            })
            valid_volumes.append(volume)
        # NOTE do not unmount the volumes or the next tasks will fail
        self._result = 'Volumes: {vv} valid, {iv} skipped'.format(
            vv=len(valid_volumes),
            iv=len(skipped_volumes),
        )
