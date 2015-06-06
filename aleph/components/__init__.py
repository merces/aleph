import logging, os
import pluginbase
from multiprocessing import Process
from aleph.base import SampleBase
from aleph.constants import SAMPLE_STATUS_PROCESSING, SAMPLE_STATUS_PROCESSED
from aleph.utils import get_path

class SampleManager(Process):
    ''' Manager Samples (load/get/sort/process/run/stop)'''
    logger = None

    sample_queue = None
    plugins = []
    plugin_source = None

    def __init__(self, sample_queue):
        super(SampleManager, self).__init__()

        self.logger = logging.getLogger(self.__class__.__name__)

        self.sample_queue = sample_queue

        self.plugins = []
        self.plugin_source = None
        self.load_plugins()

        self.logger.info('SampleManager started')

    def load_plugins(self):
        ''' Load plugins on path=aleph/plugins/'''
        self.logger.debug('Loading plugins from folder')

        plugin_base = pluginbase.PluginBase(package='aleph.plugins', searchpath=[get_path('plugins')])
        self.plugin_source = plugin_base.make_plugin_source(
            searchpath=[get_path('plugins')])

        for plugin_name in self.plugin_source.list_plugins():
            plugin = self.plugin_source.load_plugin(plugin_name)
            self.plugins.append(plugin.setup(self.sample_queue))
            self.logger.debug('Plugin "%s" loaded' % plugin_name)

        runs = 0
        max_runs = 30 # Max recursion runs before considering circular reference

        while (runs <= max_runs):
            rc = self.sort_plugins()
            if rc == 0: break
            runs += 1

        if runs == max_runs: self.logger.error('Possible circular reference in plugin chain')

    def get_plugin_index(self, name):
        for plugin in self.plugins:
            if plugin.name == name: return self.plugins.index(plugin)

        raise KeyError('Plugin %s not found in plugin list' % name)

    def sort_plugins(self):

        changed = 0 
        for plugin in self.plugins:
            max_idx = 0 
            if len(plugin.depends) != 0:
                for dep in plugin.depends:
                    idx = self.get_plugin_index(dep)
                    if idx > max_idx: max_idx = idx 
            if max_idx != 0 and max_idx+1 > self.plugins.index(plugin):
                self.logger.debug( "Inserting plugin %s at position %d" % (plugin.name, max_idx+1))
                self.plugins.remove(plugin)
                self.plugins.insert(max_idx+1, plugin)
                changed += 1

        return changed
        
    def process_sample(self):

        try:
            self.logger.info('Waiting for sample')
            sample = self.sample_queue.get()
            if sample.process:
                self.logger.info('Processing sample %s' % sample.uuid)
                sample.set_status(SAMPLE_STATUS_PROCESSING)
                self.apply_plugins(sample)
                sample.set_status(SAMPLE_STATUS_PROCESSED)
                sample.store_data()
            else:
                self.logger.info('Sample %s already processed. Updating source only.' % sample.uuid)
                sample.update_source()
        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception, e:
            raise 

    def apply_plugins(self, sample):
        for plugin in self.plugins:
            plugin.set_sample(sample)
            if plugin.can_run():
                try:
                    self.logger.debug('Applying plugin %s on sample %s' % (plugin.name, sample.uuid))
                    data = plugin.process()
                    if data and len(data) > 0:
                        sample.add_data(plugin.name, data)
                except Exception, e:
                    self.logger.error("Plugin %s failed on sample %s: %s" % (plugin.name, sample.uuid, str(e)))
                    pass
            plugin.release_sample()

    def run(self):
        self.runnable = True
        while self.runnable:
            self.process_sample()

    def stop(self):
        self.runnable = False
        if self.is_alive(): self.terminate()

    def __del__(self):
        self.stop()
