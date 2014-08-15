import os
import logging
from aleph.base import CollectorBase
from aleph.settings import SAMPLE_TRIAGE_DIR

class FileCollector(CollectorBase):

    def validate_options(self):
        if 'path' not in self.options or self.options['path'] is None:
            raise KeyError('"path" not defined for local collector')

        if not os.access(self.options['path'], os.R_OK):
            raise IOError('Path "%s" is not readable' % self.options['path'])
            

    def collect(self):
        try:
            for dirname, dirnames, filenames in os.walk(self.options['path']):
                for filename in filenames:
                    filepath = os.path.join(dirname, filename)
                    self.logger.debug("Collecting file %s from %s" % (filepath, self.options['path']))
                    self.create_sample(os.path.join(self.options['path'], filepath))
        except KeyboardInterrupt:
            pass

COLLECTOR_MAP = {
    'local': FileCollector,
}
