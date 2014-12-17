# -*- coding: utf8 -*-

from aleph.base import PluginBase
from aleph.settings import SAMPLE_TEMP_DIR
import ConfigParser
import urlparse, httplib
from urllib import urlopen

class UrlParserPlugin(PluginBase):

    name = 'urlparser'

    default_options = { 
        'enabled': True,
        'probe_url': False,
        'google_api_key': None,
    }

    mimetypes = [ 'text/url' ]

    def google_safebrowsing(self, url):

        if not self.options['google_api_key']:
            return 'N/A'

        URL = "https://sb-ssl.google.com/safebrowsing/api/lookup?client=aleph-778&key={key}&appver=1.5.2&pver=3.1&url={url}"

        response = urlopen(URL.format(key=self.options['google_api_key'], url=url)).read().decode("utf8")

        if not response:
            return ['clean']

        return response.split(',')

    def probe_url(self, url):

        urlparts = urlparse.urlparse(url, allow_fragments=True)
        if urlparts.scheme == 'https':
            conn = httplib.HTTPSConnection(urlparts.netloc)
        else:
            conn = httplib.HTTPConnection(urlparts.netloc)

        path = urlparts.path

        if urlparts.query:
            path += '?'+urlparts.query

        conn.request('HEAD', path)
        res = conn.getresponse()

        headers = dict(res.getheaders())

        # If we are being redirected, spawn a new sample from new location
        if headers.has_key('location') and headers['location'] != url:
            url_text = "[InternetShortcut]\nURL=%s" % url
            
            filename = "%s.url" % hashlib.sha256(url).hexdigest()

            temp_file = tempfile.NamedTemporaryFile(dir=SAMPLE_TEMP_DIR, suffix='_%s' % filename, delete=False)
            temp_file.write(url_text).close()

            self.create_sample(temp_file.name, filename, mimetype="text/url")

        return {
            'headers': headers,
            'version': res.version,
            'status': res.status
        }

    def process(self):

        config = ConfigParser.RawConfigParser()
        config.read(self.sample.path)

        url = config.get('InternetShortcut', 'URL')

        ret = {
            'url': url,
            }

        # Google SafeBrowsing API (needs API key and SafeBrowsing API Activated on Project)
        # ref: https://developers.google.com/safe-browsing/lookup_guide#GettingStarted
        if self.options['google_api_key']:
            ret['google_safebrowsing'] = self.google_safebrowsing(url)

        # Probe URL for additional data
        if self.options['probe_url']:
            http_info = self.probe_url(url)
            ret['http_headers'] = http_info['headers']
            ret['http_status'] = http_info['status']
            ret['http_version'] = http_info['version']

        return ret

def setup(queue):
    plugin = UrlParserPlugin(queue)
    return plugin
