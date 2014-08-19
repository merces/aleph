import logging, os
from pluginbase import PluginBase
from multiprocessing import Process
from aleph.settings import SAMPLE_STORAGE_DIR
from aleph.base import SampleBase
from aleph.utils import get_path

class SampleManager(Process):

    logger = None

    input_queue = None
    plugins = []

    def __init__(self, sample_input_queue):
        super(SampleManager, self).__init__()

        self.logger = logging.getLogger(self.__class__.__name__)

        self.input_queue = sample_input_queue

        self.load_plugins()

        self.logger.info('SampleManager started')

    def load_plugins(self):
        self.logger.debug('Loading plugins from folder')

        plugin_base = PluginBase(package='aleph.plugins', searchpath=[get_path('plugins')])
        source = plugin_base.make_plugin_source(
            searchpath=[get_path('plugins')])

        for plugin_name in source.list_plugins():
            plugin = source.load_plugin(plugin_name)
            self.plugins.append(plugin.setup(self))
            self.logger.debug('Plugin "%s" loaded' % plugin_name)

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
