import logging, os
from multiprocessing import Process
from aleph.settings import SAMPLE_STORAGE_DIR
from aleph.base import SampleBase

class SampleManager(Process):

    logger = None

    input_queue = None
    plugins = []

    def __init__(self, plugins, sample_input_queue):
        super(SampleManager, self).__init__()

        self.logger = logging.getLogger(self.__class__.__name__)

        self.input_queue = sample_input_queue

        self.plugins = plugins
        self.logger.info('SampleManager started')

    def process_sample(self):

        try:
            self.logger.info('Waiting for sample')
            sample = self.input_queue.get()
            if sample.process:
                self.logger.info('Processing sample %s' % sample.uuid)
                self.apply_plugins(sample)
                sample.store_results()
            else:
                self.logger.info('Sample %s already processed. Updating source only.' % sample.uuid)
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
        if self.is_alive(): self.terminate()

    def __del__(self):
        self.stop()
