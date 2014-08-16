# Plugins must receive the sample UUID and return a JSON object with data acquired

import uuid, magic, os, logging, binascii, hashlib
from aleph.settings import SAMPLE_TRIAGE_DIR, SAMPLE_STORAGE_DIR
from shutil import move

from time import sleep

class PluginBase(object):

    scope = None

    logger = None

    mimetypes = [] # empty = all mimetypes
    mimetypes_except = [] # used when mimetypes is set to all (empty)

    name = None
    description = None

    data = {}
    sample_id = None
    
    def __init__(self, scope):
        self.scope = scope
        if not self.name: self.name = self.__class__.__name__
        self.logger = logging.getLogger('Plugin:%s' % self.name)

    def can_run(self, sample):
        
        if len(self.mimetypes) == 0:
            if sample.mimetype in self.mimetypes_except:
                return False
        elif sample.mimetype not in self.mimetypes:
            return False

        return True

    def process(self, sample_uuid):
        raise NotImplementedError('Plugin process function not implemented')

ARCHIVE_MIMTYPES = [
    'application/x-rar-compressed',
    'application/zip',
]


class SampleBase(object):

    uuid = None
    mimetype_str = None
    mimetype = None
    path = None
    child_samples = []
    sources = []
    
    hashes = {}

    data = {}
    tags = []

    def __init__(self, path):
        self.path = path
        #self.check_duplicate()
        self.prepare_sample()
        self.store_sample()

    def add_source(self, source_name, source_path):
        sources = self.sources
        sources.append( (source_name, source_path) )
        self.sources = sources

    def add_data(self, plugin_name, data):
        for key, value in data.iteritems():
            newkey = "%s.%s" % (plugin_name, key)
            self.data[newkey] = value

    def is_archive(self):

        return (self.mimetype in ARCHIVE_MIMETYPES)

    def store_sample(self):

        sample_filename = "%s.sample" % self.hashes['sha256']
        sample_path = os.path.join(SAMPLE_STORAGE_DIR, sample_filename)
        move(self.path, sample_path)
        self.path = sample_path

    def prepare_sample(self):

        # Get mimetype
        self.mimetype = magic.from_file(self.path, mime=True)
        self.mimetype_str = magic.from_file(self.path)

        self.hashes = self.get_hashes()
        # Give it a nice uuid
        self.uuid = uuid.uuid1()

    def get_hashes(self):

        hashes = {}
        # Calculate hashes
        with open(self.path) as handle:
            filedata = handle.read()
            hashes = {
            'md5': hashlib.md5(filedata).hexdigest(),
            'sha1': hashlib.sha1(filedata).hexdigest(),
            'sha256': hashlib.sha256(filedata).hexdigest(),
            'sha512': hashlib.sha512(filedata).hexdigest(),
            'crc32': "%08X" % (binascii.crc32(filedata) & 0xFFFFFFFF),
            }
        return hashes

    def __str__(self):

        return str({
            'uuid': self.uuid,
            'path': self.path,
            'mimetype': self.mimetype,
            'mime': self.mimetype_str,
            'hashes': self.hashes,
            'data': self.data,
            'sources': self.sources,
        })

class CollectorBase(object):

    logger = None

    handle = None
    queue = None
    options = {}
    default_options = {}

    def __init__(self, options, queue):

        self.queue = queue
        self.options = dict(self.default_options.items() + options.items())

        self.logger = logging.getLogger(self.__class__.__name__)

        if not os.access(SAMPLE_TRIAGE_DIR, os.W_OK):
            raise IOError('Cannot write to triage dir: %s' % SAMPLE_TRIAGE_DIR)

        self.validate_options()

    # @@ OVERRIDE ME
    def validate_options(self):
        raise NotImplementedError('Collector option validation not implemented')

    # @@ OVERRIDE ME
    def collect(self):
        raise NotImplementedError('Collector collection routine not implemented')

    def create_sample(self, filepath, sourcepath):

        self.logger.debug('Creating sample from path %s' % filepath)
        sample = SampleBase(filepath)
        sample.add_source(self.__class__.__name__, sourcepath )
        self.queue.put(sample)
