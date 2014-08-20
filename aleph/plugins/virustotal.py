# -*- coding: utf8 -*-

from aleph.base import PluginBase
import virustotal

class VirusTotalPlugin(PluginBase):

    name = 'virustotal'
    required_options = [ 'api_key' ]

    vt = None

    def setup(self):
        
    	self.vt = virustotal.VirusTotal(self.options['api_key'],0)
   
    def process(self, sample):

        try:
            report = self.vt.get(sample.hashes['sha256'])	

            if report is None:
                report = self.vt.scan(sample.path)
                report.join()
                assert report.done() == True

            detections = []
            for antivirus, malware in report:
                if malware is not None:
                    detections.append({'av': antivirus[0], 'version': antivirus[1], 'update': antivirus[2], 'result': malware})

            return {
                'scan_id': report.id,
                'positives': report.positives,
                'total': report.total,
                'detections': detections,
            }

        except Exception, e:
            self.logger.error('Error within VirusTotal API: %s' % str(e))
            return {}
    

def setup(queue):
    plugin = VirusTotalPlugin(queue)
    return plugin
