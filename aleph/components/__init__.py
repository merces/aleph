import logging, os
from multiprocessing import Process
from aleph.settings import SAMPLE_SOURCES, SAMPLE_STORAGE_DIR, SAMPLE_TRIAGE_DIR
from aleph import collectors
from aleph.base import SampleBase

class SourceManager(Process):

    logger = None

    collectors = []
    input_queue = None
    runnable = False

    def __init__(self, sample_input_queue):
        super(SourceManager, self).__init__()
        
        self.logger = logging.getLogger(self.__class__.__name__)


        self.input_queue = sample_input_queue

        self.init_collectors()

    def init_collectors(self):

        self.logger.debug('Loading collectors from sources configuration')

        triage_collector = ('local', { 'path': SAMPLE_TRIAGE_DIR })
        SAMPLE_SOURCES.append(triage_collector)
        for source in SAMPLE_SOURCES:
            source_type = source[0]
            source_params = source[1]

            if source_type not in collectors.COLLECTOR_MAP:
                raise NotImplementedError('%s collector is not implemented.' % source_type)
            self.collectors.append(collectors.COLLECTOR_MAP[source_type](source_params, self.input_queue))
            self.logger.debug('Collector "%s" loaded' % (source_type))

    def gather_samples(self):
        for collector in self.collectors:
            collector.collect()

    def run(self):
        self.runnable = True
        while self.runnable:
            try:
                self.gather_samples()
            except Exception, e:
                raise

    def stop(self):
        self.runnable = False
        self.terminate()

    def __del__(self):
        self.stop()

class SampleManager(Process):

    logger = None

    input_queue = None
    plugins = []

    def __init__(self, plugins, sample_input_queue):
        super(SampleManager, self).__init__()

        self.logger = logging.getLogger(self.__class__.__name__)

        self.input_queue = sample_input_queue

        self.plugins = plugins
        self.logger.debug('SampleManager started')

    def process_sample(self):

        try:
            self.logger.debug('Waiting for sample')
            sample = self.input_queue.get()
            if sample.process:
                self.logger.debug('Processing sample %s' % sample.uuid)
                self.apply_plugins(sample)
                sample.store_results()
            else:
                self.logger.debug('Sample %s already processed. Updating source only.' % sample.uuid)
                sample.update_source()
        except (KeyboardInterrupt, SystemExit):
            pass

    def apply_plugins(self, sample):
        for plugin in self.plugins:
            self.logger.debug('Applying plugin %s on sample %s' % (plugin.name, sample.uuid))
            data = plugin.process(sample)
            sample.add_data(plugin.name, data)

    def run(self):
        self.runnable = True
        while self.runnable:
            self.process_sample()

    def stop(self):
        self.runnable = False
        self.terminate()

    def __del__(self):
        self.stop()
