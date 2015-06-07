import unittest
from mock import Mock
from aleph.plugins.peinfo import PEInfoPlugin

class PEInfoPluginTestCase(unittest.TestCase):

    def test_it_is_initializable(self):
        queue = Mock()
        pe = PEInfoPlugin(queue)
        self.assertIsNotNone(pe)
        self.assertIsInstance(pe, PEInfoPlugin)

        