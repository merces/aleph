DEBUG = True

SAMPLE_SOURCES = [
    ('local', {'path': '/home/pr0teus/venv/sources'}),
    #('mail', {'host': 'imap.exampl.com', 'username': 'youruser@example.com', 'password': 'yourpassword', 'root_folder': 'Inbox' })
]

PLUGIN_SETTINGS = {
    'virustotal': { 'api_key': 'c421ee91fe65695998b543c4533dc1cd58745cd293e2208a23476e4639d843b9', 'api_limit': '7' }
	
}

ELASTICSEARCH_URI = '127.0.0.1:9200'
ELASTICSEARCH_INDEX = 'samples'
ELASTICSEARCH_TRACE = False

SAMPLE_TEMP_DIR = '/home/pr0teus/venv/temp'
SAMPLE_STORAGE_DIR = '/home/pr0teus/venv/samples'

SAMPLE_MANAGERS=2 # Simultaneous sample analysis

LOGGING  = {
    'filename': 'log/aleph.log',
    'format': '%(asctime)s [%(name)s:%(funcName)s] %(levelname)s: %(message)s',
}

