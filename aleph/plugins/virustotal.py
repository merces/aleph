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
                report = self.vt.get(sample.path)
                report.join()

            detections = []
            for antivirus, malware in report:
                if malware is not None:
                    av_str = "%s %s (%s)" % antivirus
                    detections.append({'av': av_str, 'name': malware})

            return {
                'scam_id': report.id,
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
