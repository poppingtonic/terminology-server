import sys
from snomedct_terminology_server.config.settings import *  # noqa

if 'test' in sys.argv or 'test_coverage' in sys.argv:  # noqa
    DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'  # noqa
    DATABASES['default']['HOST'] = '127.0.0.1'  # noqa
    DATABASES['default']['USER'] = 'snomedct_terminology_server'  # noqa
    DATABASES['default']['PASSWORD'] = 'snomedct_terminology_server'  # noqa
