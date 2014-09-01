from zipfile import ZipFile
from tempfile import mkdtemp
from aleph.base import PluginBase
import shutil, os

from aleph.settings import SAMPLE_TEMP_DIR

class ZipArchivePlugin(PluginBase):

    mimetypes = ['application/zip']
    name = 'ziparchive'
    default_options = { 'passwords': [ 'infected', 'evil', 'virus' ] }
    
    def extract_file(self, path, dest, password=None):

        nl = []

        with ZipFile(path, 'r') as zipf:
            if password:
                zipf.setpassword(password)
            zipf.extractall(dest)
            nl = zipf.namelist()

        return nl

    def process(self, sample):

        temp_dir = mkdtemp(dir=SAMPLE_TEMP_DIR)

        self.options['passwords'].insert(0, '') # Append blank password
        current_password = None
        zip_contents = []

        for password in set(self.options['passwords']):
            current_password = password
            try:
                self.logger.debug("Uncompressing file %s with password '%s'" % (sample.path, password))
                zip_contents = self.extract_file(sample.path, temp_dir, password)
                for fname in zip_contents:
                    fpath = os.path.join(temp_dir, fname)
                    self.create_sample(fpath, sample.uuid)
                shutil.rmtree(temp_dir)
                break # Stop bruting
            except RuntimeError:
                continue # Invalid password

        ret = {} 

        if len(zip_contents) == 0:
            self.logger.error('Unable to uncompress %s. Invalid password or corrupted file' % sample.path)
            return ret

        ret['contents'] = zip_contents

        if len(current_password) > 0:
            ret['password'] = current_password

        return ret

def setup(queue):
    plugin = ZipArchivePlugin(queue)
    return plugin
