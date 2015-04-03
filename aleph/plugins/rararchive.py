from rarfile import RarFile, RarExecError, BadRarFile
from tempfile import mkdtemp
from aleph.base import PluginBase
import shutil, os, ntpath

from aleph.settings import SAMPLE_TEMP_DIR, SAMPLE_MIN_FILESIZE

class RarArchivePlugin(PluginBase):

    name = 'rararchive'
    default_options = { 'passwords': [ 'infected', 'evil', 'virus', 'malicious' ], 'enabled': True }
    mimetypes = ['application/x-rar']
    
    def extract_file(self, path, dest, password=None):

        nl = []

        with RarFile(str(path), 'r') as rarf:
            if password:
                rarf.setpassword(password)
            rarf.extractall(str(dest))
            nl = rarf.namelist()

        return nl

    def process(self):

        temp_dir = mkdtemp(dir=SAMPLE_TEMP_DIR)

        self.options['passwords'].insert(0, None) # Append blank password
        current_password = None
        rar_contents = []

        for password in set(self.options['passwords']):
            current_password = password
            try:
                self.logger.debug("Uncompressing file %s with password '%s'" % (self.sample.path, password))
                rar_contents = self.extract_file(self.sample.path, temp_dir, password)

                for fname in rar_contents:
                    fpath = os.path.join(temp_dir, fname).replace('\\', '/')
                    if os.path.isfile(fpath) and os.stat(fpath).st_size >= SAMPLE_MIN_FILESIZE:
                        head, tail = ntpath.split(fpath)
                        self.create_sample(fpath, tail)
                shutil.rmtree(temp_dir)
                break # Stop bruting
            except (RarExecError, BadRarFile):
                continue # Invalid password

        ret = {}

        # Add general tags
        self.sample.add_tag('archive')
        self.sample.add_tag('rar')

        if len(rar_contents) == 0:
            self.logger.error('Unable to uncompress %s. Invalid password or corrupted file' % self.sample.path)
            self.sample.add_tag('corrupt')
            return ret

        if current_password:
            self.sample.add_tag('password-protected')
            ret['password'] = current_password

        ret['contents'] = rar_contents
        return ret

def setup(queue):
    plugin = RarArchivePlugin(queue)
    return plugin
