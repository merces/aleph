# -*- coding: utf8 -*-

from aleph.base import PluginBase
import re

class StringsPlugin(PluginBase):

    name = 'strings'

    default_options = { 'enabled': True }
    mimetypes_except = ['application/zip']

    all_regex = ur"[%s]{4,}" % r"A-Za-z0-9/\-:.,_$%'()[\]<> " 
    url_regex = ur'(?:(?:https?|ftp):\/\/)(?:\S+(?::\S*)?@)?(?:(?!10(?:\.\d{1,3}){3})(?!127(?:\.\d{1,3}){3})(?!169\.254(?:\.\d{1,3}){2})(?!192\.168(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\x{00a1}-\x{ffff}0-9]+-?)*[a-z\x{00a1}-\x{ffff}0-9]+)(?:\.(?:[a-z\x{00a1}-\x{ffff}0-9]+-?)*[a-z\x{00a1}-\x{ffff}0-9]+)*(?:\.(?:[a-z\x{00a1}-\x{ffff}]{2,})))(?::\d{2,5})?(?:\/[^\s]*)?'
    filename_regex = r'\b([\w,%-.]+\.[A-Za-z]{3})\b'
    emailaddr_regex = r'((?:(?:[A-Za-z0-9]+_+)|(?:[A-Za-z0-9]+\-+)|(?:[A-Za-z0-9]+\.+)|(?:[A-Za-z0-9]+\++))*[A-Za-z0-9]+@(?:(?:\w+\-+)|(?:\w+\.))*\w{1,63}\.[a-zA-Z]{2,6})'

    pattern_all = re.compile(all_regex)
    pattern_url = re.compile(url_regex, re.IGNORECASE)
    pattern_filename = re.compile(filename_regex)
    pattern_emailaddr = re.compile(emailaddr_regex)

    def process(self):

        with open(self.sample.path) as f:

            file_content = f.read().decode('latin1').encode('utf8')
            all_strings = [entry.strip() for entry in self.pattern_all.findall(file_content)]
            emailaddr_strings = [entry.strip() for entry in self.pattern_emailaddr.findall(file_content)]
            url_strings = [entry.strip() for entry in self.pattern_url.findall(file_content)]
            clean_content = file_content
            for token in uri_strings+emailaddr_strings:
                clean_content = clean_content.replace(token, '')

            file_strings = [entry.strip() for entry in self.pattern_filename.findall(clean_content)]

        return {
            'all': list(set(all_strings)),
            'url': list(set(url_strings)),
            'email': list(set(emailaddr_strings)),
            'file': list(set(file_strings)),
            }

def setup(queue):
    plugin = StringsPlugin(queue)
    return plugin
