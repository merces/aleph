APP_TITLE = 'Aleph'
CSRF_ENABLED = True
BABEL_DEFAULT_TIMEZONE = 'UTC'
BABEL_DEFAULT_LOCALE = 'en'
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'pt-br': 'Brazilian Portuguese',
}
SAMPLE_STATUS_NEW = 0
SAMPLE_STATUS_PROCESSING = 1
SAMPLE_STATUS_PROCESSED = 2

ACCOUNT_DISABLED=0
ACCOUNT_ENABLED=1

ACCOUNT_SUPERUSER=0
ACCOUNT_PREMIUM=1
ACCOUNT_REGULAR=2

ITEMS_PER_PAGE = 15

MIMETYPES_ARCHIVE = [
    'application/zip',
    'application/gzip',
    'application/x-gzip',
    'application/x-rar',
    'application/tar'
]