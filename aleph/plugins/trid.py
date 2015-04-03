from aleph.base import PluginBase
import subprocess, os
import re

class TrIDPlugin(PluginBase):

    name = 'trid'
    default_options = { 'enabled': False }
    required_options = [ 'trid_path', 'triddefs_path' ]
    
    def validate_options(self):
        super(TrIDPlugin, self).validate_options()

        if not os.access(self.options['trid_path'], os.X_OK):
            raise OSError('Cannot access TrID at %s' % self.trid_path)

        if not os.access(self.options['triddefs_path'], os.R_OK):
            raise OSError('Cannot access TrID definitions file at %s' % self.triddefs_path)

    def process(self):

        proc = subprocess.Popen([self.options['trid_path'], self.sample.path, '-d:%s' % self.options['triddefs_path']], stdout=subprocess.PIPE)
        output = proc.communicate()[0]

        if proc.returncode != 0:
            self.logger.error('Sample %s could not be parsed by TrID' % self.sample.uuid)
            return {}

        lines = output.split('\n')
        p = re.compile('^([0-9]{1,3}\.[0-9]%) \((\.[A-Z0-9]{3,4})\) (.*) \(([0-9].*)\)$')

        detections = []

        for line in lines:
            line = line.strip()
            m = p.match(line)
            if m:
                detections.append({'description': m.group(3), 'extension': m.group(2), 'confidence': m.group(1)})

        if len(detections) == 0:
            detections.append({'description': 'Unknown'})

        return { 'detections': detections }

def setup(queue):
    plugin = TrIDPlugin(queue)
    return plugin
