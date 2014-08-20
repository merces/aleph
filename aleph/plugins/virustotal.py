# -*- coding: utf8 -*-

from aleph.base import PluginBase
from aleph.settings import VIRUSTOTAL_KEY
import virustotal

class VirustotalPlugin(PluginBase):

    name = 'Virustotal'
   
    def process(self, sample):
	vt = virustotal.VirusTotal(VIRUSTOTAL_KEY,0)
        report = vt.get(sample.hashes['sha256'])	
	if report is None:
           report = vt.get(sample.path)
           report.join()
        if report.done ==True:
	   return {
		'virustotal': report.id,
		'positives': report.positives,
		'total': report.total,
		'antivirus': str(list(report)),
		}
    

def setup(queue):
    plugin = VirustotalPlugin(queue)
    return plugin
