import os
import logging
from aleph.base import CollectorBase
from aleph.settings import SAMPLE_TEMP_DIR

class FileCollector(CollectorBase):
    """ Class FileCollector watch for a file appear in a specified path(settings.py/SAMPLE_SOURCES/local/path) """
    required_options = [ 'path' ]

    def validate_options(self):
        """Check if options are ok, if not try to create the path."""
        super(FileCollector, self).validate_options()

        if not os.access(self.options['path'], os.R_OK):
            try:
                os.mkdir(self.options['path'])
                self.logger.info("Directory %s created" % self.options['path'])
            except OSError, e:
                raise OSError("Unable to create sample storage dir at %s: %s" % (self.options['path'], str(e)))

    def collect(self):
        """Overrided method that listen to the specific path and create samples"""
        try:
            for dirname, dirnames, filenames in os.walk(self.options['path']):
                for filename in filenames:
                    filepath = os.path.join(dirname, filename)
                    if os.path.getsize(filepath) > 0:
                        self.logger.info("Collecting file %s from %s" % (filepath, self.options['path']))
                        self.create_sample(os.path.join(self.options['path'], filepath), (filename, None))
        except KeyboardInterrupt:
            pass

import email, imaplib, tempfile, hashlib

class MailCollector(CollectorBase):

    sleep = 60 # 1 minute

    imap_session = None

    default_options = {
        'root_folder': 'Inbox',
        'delete': True,
        'ssl': True,
        'port': 993,
    }

    required_options = [ 'host', 'username', 'password' ]

    def imap_login(self):
        """Connect to the imap Server"""
        # Log into IMAP
        if self.options['ssl']:
            self.imap_session = imaplib.IMAP4_SSL(self.options['host'], self.options['port'])
        else:
            self.imap_session = imaplib.IMAP4(self.options['host'], self.options['port'])

        rc, account = self.imap_session.login(self.options['username'], self.options['password'])

        if rc != 'OK':
            raise RuntimeError('Invalid credentials')

        # Set root folder for search
        self.imap_session.select(self.options['root_folder'])

    def process_message(self, message_parts):
        """Download the email in eml format and create the sample"""

        email_body = message_parts[0][1]
        mail = email.message_from_string(email_body)

        filename = "%s.eml" % hashlib.sha256(email_body).hexdigest()

        temp_file = tempfile.NamedTemporaryFile(dir=SAMPLE_TEMP_DIR, suffix='_%s' % filename, delete=False)
        temp_file.write(email_body)
        temp_file.close()
        
        self.create_sample(temp_file.name, (filename, mail['from']))

    def collect(self):
        """Overrided method that listen to new e-mails and create new sample"""
        try:
            rc, data = self.imap_session.search(None, '(UNSEEN)')
            if rc != 'OK':
                raise RuntimeError('Error searching folder %s' % self.options['root_folder'])

            # Iterate over all messages
            for message_id in data[0].split():
                rc, message_parts = self.imap_session.fetch(message_id, '(RFC822)')
                if rc != 'OK':
                    raise RuntimeError('Error fetching message.')

                self.process_message(message_parts)
                if self.options['delete']:
                    rc, flags_msg = self.imap_session.store(message_id, '+FLAGS', r'\Deleted')
                    if rc != 'OK':
                        raise RuntimeError('Error deleting message')

            if self.options['delete']:
                rc, ids = self.imap_session.expunge()
                if rc != 'OK':
                    raise RuntimeError('Error running expunge')
            
        except Exception, e:
            raise


    def setup(self):
        try:
            self.imap_login()

        except Exception, e:
            return RuntimeError('Cannot connect to server: %s' % str(e))

    def teardown(self):
        if self.imap_session:
            self.imap_session.close()
            self.imap_session.logout()


COLLECTOR_MAP = {
    'local': FileCollector,
    'mail': MailCollector,
}
