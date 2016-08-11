import sys
from snomedct_terminology_server.config.settings import *

if 'test' in sys.argv or 'test_coverage' in sys.argv:  # Covers regular testing and django-coverage
    DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
    DATABASES['default']['HOST'] = '127.0.0.1'
    DATABASES['default']['USER'] = 'snomedct_terminology_server'
    DATABASES['default']['PASSWORD'] = 'snomedct_terminology_server'