from aleph.base import PluginBase
import subprocess, os

class TrIDPlugin(PluginBase):

    name = 'trid'

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

        lines = output.split('\n')[6:-1]

        detections = []

        for line in lines:
            parts = line.strip().split(' ')
            percentage = parts[0]
            extension = parts[1][1:-1]
            name = ' '.join(parts[2:-1])

            detections.append({'name': name, 'extension': extension, 'confidence': percentage})


        if len(detections) > 0:
            return { 'detections': detections }

def setup(queue):
    plugin = TrIDPlugin(queue)
    return plugin
