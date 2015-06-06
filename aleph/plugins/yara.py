# -*- coding: utf8 -*-

from aleph.base import PluginBase
from aleph.utils import in_string
from aleph.constants import MIMETYPES_ARCHIVE
from operator import itemgetter
import yara

class YaraPlugin(PluginBase):

    name = 'yara'
    default_options = { 'enabled': True}  
    required_options = [ 'rules_path']

    rules = None
      
    def setup(self):
        try:
            self.rules = yara.compile(filepath=self.options['rules_path'])
        except Exception, e:
            self.logger.warning('YARA could not read the rules: %s ' % (str(self.options['rules_path'])))

    def process(self):
        try:
            matches = self.rules.match(self.sample.path)
        except Exception, e:
            self.logger.warning('Error matching: %s ' % (str(e)))
        return {
                'yara_rules':self.options['rules_path'],
                'matches': matches
                }



def setup(queue):
    plugin = YaraPlugin(queue)
    return plugin
