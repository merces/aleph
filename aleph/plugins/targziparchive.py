import tarfile
from tempfile import mkdtemp
from aleph.base import PluginBase
import shutil, os, ntpath

from aleph.settings import SAMPLE_TEMP_DIR

class TarGzipArchivePlugin(PluginBase):

    name = 'archive_tar-gzip'
    default_options = { 'enabled': True }
    mimetypes = ['application/x-tar', 'application/gzip']
    
    def extract_file(self, path, dest):

        nl = []

        with tarfile.open(path, 'r') as tarf:
            tarf.extractall(dest)
            nl = tarf.getnames()

        return nl

    def process(self):

        temp_dir = mkdtemp(dir=SAMPLE_TEMP_DIR)

        targzip_contents = []

        self.logger.debug("Uncompressing gzip/tar file %s" % self.sample.path)
        targzip_contents = self.extract_file(self.sample.path, temp_dir)
        for fname in targzip_contents:
            fpath = os.path.join(temp_dir, fname)
            if os.path.isfile(fpath):
                head, tail = ntpath.split(fpath)
                self.create_sample(fpath, tail)
        shutil.rmtree(temp_dir)

        ret = {} 

        if len(targzip_contents) == 0:
            self.logger.error('Unable to uncompress %s. Corrupted file?' % self.sample.path)
            return ret

        ret['contents'] = targzip_contents

        # Add general tags
        self.sample.add_tag('archive')
        self.sample.add_tag('tar-gzip')

        return ret

def setup(queue):
    plugin = TarGzipArchivePlugin(queue)
    return plugin
