import PIL.Image

from ..basetask import BaseTask
from .. import utils


logger = utils.get_logger(__name__)


class JpegFile(BaseTask):

    MAGIC_PATTERN = '^JPEG image data.*'

    def __init__(self, path, *args, **kwargs):
        BaseTask.__init__(self, path, *args, **kwargs)

    def run(self):
        # Extract EXIF data
        # TODO Extract IPTC info too
        # TODO Extract non-exif comments (i.e. fields starting with \xff\xfe)
        image = PIL.Image.open(self._path)
        tags = image._exiftags()
        image.close()
        msg = 'Extracted {n} EXIF tags from {p!r}'.format(
            n=len(tags),
            p=self._path,
        )
        logger.info(msg)
        self._result = msg
