from zipfile import ZipFile
from tempfile import mkdtemp
from aleph.base import PluginBase
import shutil, os

from aleph.settings import SAMPLE_TEMP_DIR

class ZipArchivePlugin(PluginBase):

    mimetypes = ['application/zip']
    name = 'ziparchive'
    
    def process(self, sample):
        temp_dir = mkdtemp(dir=SAMPLE_TEMP_DIR)
        with ZipFile(sample.path, 'r') as zipf:
            zipf.extractall(temp_dir)
            for fname in zipf.namelist():
                fpath = os.path.join(temp_dir, fname)
                self.create_sample(fpath, sample.uuid)

        shutil.rmtree(temp_dir)

        return {
            'contents': zipf.namelist()
            }

def setup(queue):
    plugin = ZipArchivePlugin(queue)
    return plugin
