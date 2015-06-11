# -*- coding: utf8 -*-
import unittest
from mock import Mock
from aleph.plugins.yara import YaraPlugin

class YaraPluginTestCase(unittest.TestCase):

	yara_rules_path = 'data/test_yara_rules.yar'

		def test_if_its_initializabe(self):
			queue = Mock()
			
			yara_plugin = YaraPlugin(queue)
			self.assert

		def test_if_process_is_matching(self):
			response = {
						'yara_rules':self.yara_rules_path,
                		'matches': matches
						}
			sample_path = 'data/sample.exe'
			yara_plugin = YaraPlugin(queue)
			yara_plugin.sample = sample_path
			self.assertDictEqual(response,yara_plugin.process())