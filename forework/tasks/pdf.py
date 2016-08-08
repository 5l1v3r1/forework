import os
# import json
# import zlib
import tempfile
import subprocess

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1

from ..basetask import BaseTask
from .directoryscanner import DirectoryScanner
from .. import utils


logger = utils.get_logger(__name__)


class PDFFile(BaseTask):

    MAGIC_PATTERN = '^PDF document.*'
    MODIFIERS = [
        'extract_pictures',
        'outdir',
    ]

    def __init__(self, path, config, *args, **kwargs):
        BaseTask.__init__(self, path, config, *args, **kwargs)

    def run(self):
        with open(self._path, 'rb') as fd:
            parser = PDFParser(fd)
            doc = PDFDocument(parser)

            # Get the /Info object
            info = str(doc.info) or '<empty>'

            # Get the /Metadata object
            metadata = '<empty>'
            if 'Metadata' in doc.catalog:
                metadata = str(resolve1(doc.catalog['Metadata']).get_data())

            # check the modifiers
            extracted_images = []
            outdir = None
            if self.conf['extract_pictures']:
                if self.conf['outdir']:
                    outdir = self.conf['outdir']
                else:
                    outdir = tempfile.mkdtemp(prefix=self.conf)
                try:
                    os.makedirs(outdir)
                except FileExistsError:
                    logger.warning('Directory {d!r} already exists, going '
                                   'ahead anyway'.format(d=outdir))

                # TODO horrible hack, in need for a pure Python implementation
                prefix = os.path.join(outdir, self._config.name)
                subprocess.check_call(['pdfimages', '-j', self._path, prefix])
                extracted_images = os.listdir(outdir)
                self.add_next_task({
                    'name': [DirectoryScanner.__name__],
                    'path': outdir,
                })

        self._result = {
            'Info': info,
            'Metadata': metadata,
            'images': extracted_images,
            'outdir': outdir,
        }
