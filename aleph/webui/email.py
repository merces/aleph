from flask.ext.mail import Message
from aleph.webui import mail
from . import app
import logging

logger = logging.getLogger('Email')

def send_email(subject, sender, recipients, text_body, html_body):
    if not app.config.get('MAIL_ENABLE'):
        if app.config.get('DEBUG'):
            logger.debug('Mail functions are disabled. Check MAIL_ENABLE config option.')
        return False

    try:
        msg = Message(subject, sender = sender, recipients = recipients)
        msg.body = text_body
        msg.html = html_body
        mail.send(msg)
        return True
    except Exception, e:
        logger.error('Error sending email: %s' % str(e))
        return False
