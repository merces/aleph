from aleph.base import PluginBase
import re

class StringsPlugin(PluginBase):

    name = 'strings'

    def process(self, sample):
        if not self.can_run(sample): return False

        chars = r"A-Za-z0-9/\-:.,_$%'()[\]<> "
        shortest_run = 4
        regexp = '[%s]{%d,}' % (chars, shortest_run)
        pattern = re.compile(regexp)

        strings = []
        with open(sample.path) as f:

            strings = [entry.strip() for entry in pattern.findall(f.read())]

        return {'strings': strings}

def setup(app):
    plugin = StringsPlugin(app)
    return plugin
