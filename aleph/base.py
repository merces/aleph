from multiprocessing import Process
import uuid, magic, os, logging, binascii, hashlib, time, datetime, ssdeep
from aleph.datastore import es
from aleph.settings import SAMPLE_STORAGE_DIR, PLUGIN_SETTINGS, SAMPLE_MIN_FILESIZE, SAMPLE_MAX_FILESIZE
from aleph.constants import SAMPLE_STATUS_NEW
from aleph.utils import to_iso8601, humansize
from shutil import move

from time import sleep

class PluginBase(object):

    logger = None

    mimetypes = [] # empty = all mimetypes
    mimetypes_except = [] # used when mimetypes is set to all (empty)

    name = None
    description = None

    options = {}
    default_options = {}
    required_options = []

    depends = []

    queue = None

    sample = None
    

    def __init__(self, queue):
        if not self.name: self.name = self.__class__.__name__
        self.logger = logging.getLogger('Plugin:%s' % self.name)

        self.queue = queue
        self.sample = None

        options = PLUGIN_SETTINGS[self.name] if self.name in PLUGIN_SETTINGS else {}
        self.options = dict(self.default_options.items() + options.items())

        if 'enabled' not in self.options:
            self.options['enabled'] = False
        
        if self.options['enabled']:
            self.validate_options()
            self.setup()

    # @@ OVERRIDE ME
    def setup(self):
        return True

    # @@ OVERRIDE ME
    def validate_options(self):
        self.check_required_options()

    def check_required_options(self):
        for option in self.required_options:
            if option not in self.options or self.options[option] is None:
                raise KeyError('Parameter "%s" not defined for %s plugin' % (option, self.__class__.__name__))

    def can_run(self):
        
        if not self.options['enabled']:
            return False

        if not self.sample:
            return False

        if len(self.mimetypes) == 0:
            if self.sample.mimetype in self.mimetypes_except:
                return False
        elif self.sample.mimetype not in self.mimetypes:
            return False

        return True

    def process(self):
        raise NotImplementedError('Plugin process function not implemented')

    def release_sample(self):
        self.sample = None

    def set_sample(self, sample):
        self.sample = sample

    def create_sample(self, filepath, filename, mimetype=None):

        self.logger.debug('Creating sample from path %s' % filepath)

        sample = SampleBase(filepath, mimetype)

        # Save source
        sample.add_source(self.__class__.__name__, filename, self.sample.uuid)

        # Store XREF relations
        self.sample.add_xref('child', sample.uuid)
        sample.add_xref('parent', self.sample.uuid)

        sample.store_data()
        self.sample.store_data()
        self.queue.put(sample)

        return True

class SampleBase(object):

    uuid = None
    mimetype_str = None
    mimetype = None
    path = None
    sources = []
    timestamp = None
    process = False

    status = SAMPLE_STATUS_NEW;

    xrefs = {
        'parent': [],
        'child': [],
    }
    
    hashes = {}

    size = 0

    data = {}
    tags = []

    def __init__(self, path, mimetype=None):

        self.path = path
        self.data = {}
        self.sources = []
        self.tags = []
        self.hashes = self.get_hashes()
        self.timestamp = to_iso8601()
        self.mimetype = mimetype

        self.status = SAMPLE_STATUS_NEW;
        self.xrefs = {
            'parent': [],
            'child': [],
        }


        # Size boundary check
        sample_size = os.stat(path).st_size 

        if sample_size > SAMPLE_MAX_FILESIZE:
            os.unlink(path)
            raise ValueError('Sample %s (%s) is bigger than maximum file size allowed: %s' % (path, humansize(sample_size), humansize(SAMPLE_MAX_FILESIZE)))

        if sample_size < SAMPLE_MIN_FILESIZE:
            os.unlink(path)
            raise ValueError('Sample %s (%s) is smaller than minimum file size allowed: %s' % (path, humansize(sample_size), humansize(SAMPLE_MIN_FILESIZE)))

        if not self.check_exists():
            self.store_sample()
            self.prepare_sample()
            self.store_data()

    def dispose(self):
        os.unlink(self.path)

    def set_status(self, status):
        self.status = status
        es.update(self.uuid, {'status': self.status})

    def update_source(self):
        source_set = self.sources
        es.update(self.uuid, {'sources': source_set})

    def check_exists(self):

        result = es.search({"hashes.sha256": self.hashes['sha256']})
        exists = ('hits' in result and result['hits']['total'] != 0)
        if exists:
            data = result['hits']['hits'][0]['_source']
            self.uuid = data['uuid']
            self.sources = data['sources']
            self.dispose()

        return exists

    def add_xref(self, relation, sample_uuid):

        xrefs = self.xrefs

        if relation not in [ 'parent', 'child' ]:
            raise KeyError('XRef Relation must be either \'parent\' or \'child\'')

        if sample_uuid not in xrefs[relation] and self.uuid != sample_uuid:
            xrefs[relation].append(sample_uuid)
            self.xrefs = xrefs

    def add_source(self, provider, filename, reference=None):
        sources = self.sources
        sources.append( {'timestamp': to_iso8601(), 'provider': provider, 'filename': filename, 'reference': reference} )
        self.sources = sources

    def add_tag(self, tag_name):
        if tag_name not in self.tags:
            tags = self.tags
            tags.append(tag_name)
            self.tags = tags

    def add_data(self, plugin_name, data):

        self.data[plugin_name] = data

    def store_sample(self):

        sample_filename = "%s.sample" % self.hashes['sha256']
        sample_path = os.path.join(SAMPLE_STORAGE_DIR, sample_filename)
        move(self.path, sample_path)
        self.path = sample_path

    def prepare_sample(self):

        # Get mimetype if not supplied
        if not self.mimetype:
            self.mimetype = magic.from_file(self.path, mime=True)
            self.mimetype_str = magic.from_file(self.path)
        
        # Get file size
        self.size = os.stat(self.path).st_size

        # Give it a nice uuid
        self.uuid = str(uuid.uuid1())

        # Let it process
        self.process = True

    def store_data(self):
        es.save(self.toObject(), self.uuid)

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
            'ssdeep': ssdeep.hash(filedata),
            }
        return hashes

    def toObject(self):
        return {
            'uuid': self.uuid,
            'status': self.status,
            'path': self.path,
            'mimetype': self.mimetype,
            'mime': self.mimetype_str,
            'hashes': self.hashes,
            'data': self.data,
    	    'tags': self.tags,
    	    'timestamp' : self.timestamp,	
            'sources': self.sources,
            'size': self.size,
            'xrefs': self.xrefs
        }

    def __str__(self):

        return str(self.toObject)

class CollectorBase(Process):

    logger = None

    handle = None
    queue = None
    options = {}
    default_options = {}
    required_options = []

    sleep = 5.0

    def __init__(self, options, queue):

        super(CollectorBase, self).__init__()

        self.queue = queue
        self.options = dict(self.default_options.items() + options.items())

        if 'sleep' in self.options: self.sleep = float(self.options['sleep'])

        self.logger = logging.getLogger(self.__class__.__name__)

        try:
            if not os.access(SAMPLE_STORAGE_DIR, os.W_OK):
                raise IOError('Cannot write to storage dir: %s' % SAMPLE_STORAGE_DIR)

            self.validate_options()
            self.setup()

        except Exception, e:
            self.logger.error('Error starting collector %s: %s' % (self.__class__.__name__, str(e)))

    def run(self):
        self.runnable = True
        self.logger.info('%s collector started' % self.__class__.__name__)
        while self.runnable:
            try:
                self.collect()
                sleep(self.sleep)
            except Exception, e:
                raise e

    def stop(self):
        self.runnable = False
        self.terminate()

    def __del__(self):
        self.teardown()
        self.stop()

    def check_required_options(self):
        for option in self.required_options:
            if option not in self.options or self.options[option] is None:
                raise KeyError('Parameter "%s" not defined for %s collector' % (option, self.__class__.__name__))

    # @@ OVERRIDE ME
    def teardown(self):
        return True

    # @@ OVERRIDE ME
    def setup(self):
        return True

    # @@ OVERRIDE ME
    def validate_options(self):
        self.check_required_options()

    # @@ OVERRIDE ME
    def collect(self):
        raise NotImplementedError('Collector collection routine not implemented')

    def create_sample(self, filepath, sourcedata, mimetype=None):

        self.logger.debug('Creating sample from path %s (source: %s)' % (filepath, sourcedata[0]))

        sample = SampleBase(filepath, mimetype)
        sample.add_source(self.__class__.__name__, sourcedata[0], sourcedata[1] )

        if sample.process:
            sample.store_data()
        self.queue.put(sample)
