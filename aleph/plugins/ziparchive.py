from zipfile import ZipFile
from tempfile import mkdtemp
from aleph.base import PluginBase
import shutil, os, ntpath

from aleph.settings import SAMPLE_TEMP_DIR, SAMPLE_MIN_FILESIZE

class ZipArchivePlugin(PluginBase):

    name = 'ziparchive'
    default_options = { 'passwords': [ 'infected', 'evil', 'virus', 'malicious' ], 'enabled': True }
    mimetypes = ['application/zip']
    
    def extract_file(self, path, dest, password=None):

        nl = []

        with ZipFile(str(path), 'r') as zipf:
            if password:
                zipf.setpassword(password)
            zipf.extractall(str(dest))
            nl = zipf.namelist()

        return nl

    def process(self):

        temp_dir = mkdtemp(dir=SAMPLE_TEMP_DIR)

        self.options['passwords'].insert(0, '') # Append blank password
        current_password = None
        zip_contents = []

        for password in set(self.options['passwords']):
            current_password = password
            try:
                self.logger.debug("Uncompressing file %s with password '%s'" % (self.sample.path, password))
                zip_contents = self.extract_file(self.sample.path, temp_dir, password)

                for fname in zip_contents:
                    fpath = os.path.join(temp_dir, fname)
                    if os.path.isfile(fpath) and os.stat(fpath).st_size >= SAMPLE_MIN_FILESIZE:
                        head, tail = ntpath.split(fpath)
                        self.create_sample(fpath, tail)
                shutil.rmtree(temp_dir)
                break # Stop bruting
            except RuntimeError:
                continue # Invalid password

        ret = {}

        # Add general tags
        self.sample.add_tag('archive')
        self.sample.add_tag('zip')

        if len(zip_contents) == 0:
            self.logger.error('Unable to uncompress %s. Invalid password or corrupted file' % self.sample.path)
            self.sample.add_tag('corrupt')
            return ret

        ret['contents'] = zip_contents

        if len(current_password) > 0:
            self.sample.add_tag('password-protected')
            ret['password'] = current_password

        return ret

def setup(queue):
    plugin = ZipArchivePlugin(queue)
    return plugin
