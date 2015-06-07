# -*- coding: utf8 -*-

from aleph.base import PluginBase
from aleph.settings import SAMPLE_TEMP_DIR
import email, tempfile

class EmailPlugin(PluginBase):
    """Plugin that analyze eml file getting headers, from, to and subjct of the e-mail"""
    name = 'email'
    default_options = { 'enabled': True }
    mimetypes = ['message/rfc822']

    def process(self):

        with open(self.sample.path) as f:

            file_content = f.read()
            mail = email.message_from_string(file_content)

            # Get attachments
            for part in mail.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                filename = part.get_filename()
     
                if bool(filename):
                    temp_file = tempfile.NamedTemporaryFile(dir=SAMPLE_TEMP_DIR, suffix='_%s' % filename, delete=False)
                    temp_file.write(part.get_payload(decode=True))
                    self.create_sample(temp_file.name, filename)


        headers = []
        for item in mail.items():
            headers.append({'name': item[0], 'value': item[1]})

        return {
            'headers': headers,
            'from': mail.get('From'),
            'to': mail.get('To'),
            'subject': mail.get('Subject'),
            }

def setup(queue):
    plugin = EmailPlugin(queue)
    return plugin
