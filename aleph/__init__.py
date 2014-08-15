#!/usr/bin/env python

import os, sys, logging
from pluginbase import PluginBase
from multiprocessing import Process, Queue

from aleph import utils, settings, collectors
from aleph.components import SourceManager, SampleManager

class AlephServer(object):

    # Properties
    logger = None

    running = False

    director = None
    source_manager = None
    sample_manager = None

    sample_in_queue = None
    sample_out_queue = None

    plugin_base = None
    plugin_source = None
    plugins = []

    def __init__(self):
        self.init_logger()
        self.sample_in_queue = Queue()
        self.sample_out_queue = Queue()

    def __del__(self):
        self.stop_services()

    def load_plugins(self):
        self.logger.debug('Loading plugins from folder')

        plugin_base = PluginBase(package='aleph.plugins', searchpath=[utils.get_path('./plugins')])
        self.source = plugin_base.make_plugin_source(
            searchpath=[utils.get_path('./plugins')])

        for plugin_name in self.source.list_plugins():
            plugin = self.source.load_plugin(plugin_name)
            self.plugins.append(plugin.setup(self))
            self.logger.debug('Plugin "%s" loaded' % plugin_name)

    def init_logger(self):

        log_level = logging.DEBUG if settings.DEBUG else logging.INFO

        logging.basicConfig(
            filename=settings.LOGGING['filename'],
            level=log_level,
            format=settings.LOGGING['format'],
            )

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('Logger module initialized')

    def stop_services(self):
        if self.source_manager: self.source_manager.stop()
        if self.sample_manager: self.sample_manager.stop()
        
    def init_source_manager(self):

        self.source_manager = SourceManager(self.sample_in_queue)
        self.source_manager.start()

    def init_sample_manager(self):

        self.sample_manager = SampleManager(self.plugins, self.sample_in_queue)
        self.sample_manager.start()

    def run(self):
        print 'Starting AlephServer'
        self.logger.info('Starting AlephServer')
        self.load_plugins()

        self.running = True
        try:
            while self.running:
                if not self.source_manager: #  or not self.source_manager.is_alive():
                    self.init_source_manager()

                if not self.sample_manager: #  or not self.source_manager.is_alive():
                    self.init_sample_manager()

        except (KeyboardInterrupt, SystemExit):
            print "CTRL+C received. Killing all workers"
            self.running = False
            self.stop_services()
