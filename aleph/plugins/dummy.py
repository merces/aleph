from aleph.base import PluginBase
class MockPlugin(PluginBase):

    def process(self, sample):
        self.logger.debug('Testing log from plugin')
        return {'mock': 'yay'}

def setup(app):
    plugin = MockPlugin(app)
    return plugin
