import unittest
from mock import Mock
from aleph.plugins.peinfo import PEInfoPlugin

class PEInfoPluginTestCase(unittest.TestCase):

    def test_it_is_initializable(self):
        queue = Mock()
        pe = PEInfoPlugin(queue)
        self.assertIsNotNone(pe)
        self.assertIsInstance(pe, PEInfoPlugin)

    def test_it_get_pe_data(self):
        response = {'compilation_date': '2009-07-14 01:12:13', 'aslr': True, 'dep': True, 'architechture': '32-bit', 'number_sections': 1, 'compilation_timestamp': 1247533933, 'sections': [{'virtual_size': '0x538', 'name': '.rsrc', 'raw_size': 1536, 'address': '0x1000'}], 'seh': True}
    	queue = Mock()
    	sample = Mock()
    	sample.path = 'test/data/wmerror.dll'
        pe = PEInfoPlugin(m)
        pe.set_sample(sample)
        self.assertDictEqual(response, pe.get_pe_data())

        