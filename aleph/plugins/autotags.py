'# -*- coding: utf8 -*-'

from aleph.base import PluginBase

class AutoTagsPlugin(PluginBase):

    name = 'tags'
    depends = ['virustotal']	
    
    def process(self, sample):
    	self.rules(sample)


    def add_tags(self, sample, tag):
	if self.HasTag(sample,tag) == False:
		sample.tags.append(tag)


    def del_tags(sample, tag):
	if self.HasTag(sample,tag) == False:
		sample.tags.remove(tag)


    def HasTag(self, sample, tag):
	if(tag in sample.tags):
		return True
	else:
		return False

    def rules(self, sample):
	if 'virustotal' in sample.data:
		if len(sample.data['virustotal']['detections']) > 0:
			self.add_tags(sample, 'malware')


def setup(queue):
    plugin = AutoTagsPlugin(queue)
    return plugin

