DEBUG = True
SAMPLE_SOURCES = [
    #('local', {'path': '/some/path'}),
    #('mail', {'host': 'imap.exampl.com', 'username': 'youruser@example.com', 'password': 'yourpassword', 'root_folder': 'Inbox' })
]
ELASTICSEARCH_URL = '10.1.1.173:9200'
ELASTICSEARCH_INDEX = 'samples'
ELASTICSEARCH_TRACE = False
SAMPLE_TRIAGE_DIR = '/tmp/samples_triage'
SAMPLE_TEMP_DIR = '/tmp/samples_temp'
SAMPLE_ANALYSIS_DIR = '/tmp/samples_analysis'
SAMPLE_STORAGE_DIR = '/tmp/samples_storage'
LOGGING  = {
    'filename': 'log/aleph.log',
    'format': '%(asctime)s [%(name)s:%(funcName)s] %(levelname)s: %(message)s',
}
