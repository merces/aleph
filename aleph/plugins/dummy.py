from aleph.base import PluginBase
class MockPlugin(PluginBase):
    
    depends = ['strings']

    def process(self, sample):
        self.logger.debug('Testing log from plugin')
        return {'mock': 'yay'}

def setup(queue):
    plugin = MockPlugin(queue)
    return plugin
