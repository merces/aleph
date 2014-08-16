DEBUG = True
SAMPLE_SOURCES = [
    #('local', {'path': '/some/path'}),
    #('mail', {'host': 'imap.gmail.com', 'username': 'aleph.samples@gmail.com', 'password': 'YOURPASSWORDHERE', 'root_folder': 'Inbox' })
]
ELASTICSEARCH_URL = 'http://10.1.1.173:9200/'
SAMPLE_TRIAGE_DIR = '/tmp/samples_triage'
SAMPLE_TEMP_DIR = '/tmp/samples_temp'
SAMPLE_ANALYSIS_DIR = '/tmp/samples_analysis'
SAMPLE_STORAGE_DIR = '/tmp/samples_storage'
LOGGING  = {
    'filename': 'log/aleph.log',
    'format': '%(asctime)s [%(name)s:%(funcName)s] %(levelname)s: %(message)s',
}
