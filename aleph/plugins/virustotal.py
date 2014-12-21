# -*- coding: utf8 -*-

from time import sleep
from aleph.base import PluginBase
from aleph.utils import in_string
from aleph.constants import MIMETYPES_ARCHIVE
import virustotal

class VirusTotalPlugin(PluginBase):

    name = 'virustotal'
    default_options = { 'api_limit': 7, 'retry_count': 3, 'retry_sleep': 10, 'report_sleep': 60, 'enabled': False }
    required_options = [ 'api_key' ]
    mimetypes_except = MIMETYPES_ARCHIVE + ['text/url']

    vt = None

    def setup(self):
        
    	self.vt = virustotal.VirusTotal(self.options['api_key'],self.options['api_limit'])
   
    def process(self):

        count = int(self.options['retry_count'])

        for i in range(count):
            try:
                report = self.vt.get(self.sample.hashes['sha256'])	

                if report is None:
                    report = self.vt.scan(self.sample.path)
                    sleep(self.options['report_sleep'])
                    report.join()

                    assert report.done() == True

                detections = []
                for antivirus, malware in report:
                    if malware is not None:

                            self.parse_tags(malware)
                            detections.append({'av': antivirus[0], 'version': antivirus[1], 'update': antivirus[2], 'result': malware})

                if len(detections) > 0:
                    self.sample.add_tag('malware')

                return {
                    'scan_id': report.id,
                    'positives': report.positives,
                    'total': report.total,
                    'detections': detections,
                }

            except Exception, e:
                self.logger.warning('Error within VirusTotal API: %s (retrying in %s seconds [%d/%d])' % (str(e), self.options['retry_sleep'], i, count ))
                sleep(self.options['retry_sleep'])
                continue # silently ignore errors

        self.logger.error('Error within VirusTotal API: %s (failed - no more retries left)' % str(e))
        return {}

    def parse_tags(self, malware_name):

        if in_string([ 'banker', 'banload' ], malware_name):
            self.sample.add_tag('banker')

        if in_string([ 'trojan' ], malware_name):
            self.sample.add_tag('trojan')


def setup(queue):
    plugin = VirusTotalPlugin(queue)
    return plugin
