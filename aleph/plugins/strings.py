# -*- coding: utf8 -*-

from aleph.base import PluginBase
from aleph.constants import MIMETYPES_ARCHIVE
import re

class StringsPlugin(PluginBase):
    """Try to Extract Strings from the sample (URL/filesnames/e-mails) just like the unix command strings"""
    name = 'strings'
    default_options = { 'enabled': True }
    mimetypes_except = MIMETYPES_ARCHIVE + ['text/url']

    url_regex = ur'(?i)\b((?:http[s]?:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s!()\[\]{};:\'".,<>?]))'
    filename_regex = r'\b([\w,%-.]+\.[A-Za-z]{3,4})\b'
    emailaddr_regex = r'((?:(?:[A-Za-z0-9]+_+)|(?:[A-Za-z0-9]+\-+)|(?:[A-Za-z0-9]+\.+)|(?:[A-Za-z0-9]+\++))*[A-Za-z0-9]+@(?:(?:\w+\-+)|(?:\w+\.))*\w{1,63}\.[a-zA-Z]{2,6})'

    pattern_url = re.compile(url_regex, re.IGNORECASE)
    pattern_filename = re.compile(filename_regex)
    pattern_emailaddr = re.compile(emailaddr_regex)

    def extract_strings(self, data):
        result = ""
        for c in data:
            if c in string.printable:
                result += c
                continue
            if len(result) >= min:
                yield result
            result = ""

    def process(self):

        with open(self.sample.path) as f:

            string_list = self.extract_strings(f.read())

            emailaddr_strings = []
            url_strings = []
            file_strings = []

            for found in string_list:
                emailaddr_strings += [entry.strip() for entry in self.pattern_emailaddr.findall(found)]
                url_strings += [entry[0].strip() for entry in self.pattern_url.findall(found)]
                clean_content = found

            for token in url_strings+emailaddr_strings:
                clean_content = clean_content.replace(token, '')

            file_strings += [entry.strip() for entry in self.pattern_filename.findall(clean_content)]
        
        return {
            'all': list(set(string_list)),
            'url': list(set(url_strings)),
            'email': list(set(emailaddr_strings)),
            'file': list(set(file_strings)),
            }

def setup(queue):
    plugin = StringsPlugin(queue)
    return plugin
