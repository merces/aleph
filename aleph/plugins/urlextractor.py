# -*- coding: utf8 -*-

from aleph.base import PluginBase
from aleph.settings import SAMPLE_TEMP_DIR
import tempfile, hashlib

class UrlExtractorPlugin(PluginBase):

    name = 'urlextractor'

    default_options = { 'enabled': True }
    depends = [ 'strings' ]

    def process(self):

        if not 'strings' in self.sample.data:
            return {} 

        strs = self.sample.data['strings']

        if 'url' in strs and len(strs['url']) > 0:
            for url in strs['url']:
                url_text = "[InternetShortcut]\nURL=%s" % url
                
                filename = "%s.url" % hashlib.sha256(url).hexdigest()

                temp_file = tempfile.NamedTemporaryFile(dir=SAMPLE_TEMP_DIR, suffix='_%s' % filename, delete=False)
                temp_file.write(url_text)
                temp_file.close()

                self.create_sample(temp_file.name, filename, mimetype="text/url")

        return {
            'headers': mail.items(),
            'from': mail.get('From'),
            'to': mail.get('To'),
            'subject': mail.get('Subject'),
            }

def setup(queue):
    plugin = UrlExtractorPlugin(queue)
    return plugin
