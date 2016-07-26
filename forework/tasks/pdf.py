import os
# import json
# import zlib
import tempfile
import subprocess

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1

from ..basetask import BaseTask
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
            info = doc.info or '<empty>'

            # Get the /Metadata object
            metadata = '<empty>'
            if 'Metadata' in doc.catalog:
                metadata = resolve1(doc.catalog['Metadata']).get_data()

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

#                visited = set()
#                for xref in doc.xrefs:
#                    for obj_id in xref.get_objids():
#                        if obj_id in visited:
#                            continue
#                        visited.add(obj_id)
#
#                        obj = doc.getobj(obj_id)
#                        if 'Subtype' in obj and obj['Subtype'].name == 'Image':
#                            # NOTE: checking that obj['Type'] is XObject is
#                            #       optional according to the PDF specs
#                            img_info = {
#                                'width': obj['Width'],  # mandatory
#                                'height': obj['Height'],  # mandatory
#                            }
#                            extracted_images.append(img_info)
#                            if obj['Filter'].name == 'FlateDecode':
#                                stream = zlib.decompress(obj.rawdata)
#                            else:
#                                img_dict = dict(metadata)  # copy the object
#                                img_dict.update({
#                                    'filter': obj['Filter'].name,
#                                    'stream': obj.rawdata,
#                                })
#                                stream = json.dumps(img_dict)
#                            outfile = tempfile.NamedTemporaryFile(
#                                prefix='pdf_img_',
#                                dir=outdir,
#                                delete=False,
#                            )
#                            outfile.write(stream)
#                            outfile.close()

        self._result = {
            'Info': info,
            'Metadata': metadata,
            'images': extracted_images,
            'outdir': outdir,
        }
