"""Terminology API server project settings"""
# -coding=utf-8
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '36o32ca(s_*hzwh5*8snp($fajwwl&j%d08^xcnes4j-0rx$#3'
DEBUG = True
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['.slade360.co.ke', '.localhost', '.savannahinformatics.com']
INSTALLED_APPS = (
    # Built in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'gunicorn',
    'core.apps.CoreConfig',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
)
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'termserver',
        'USER': 'termserver',
        'PASSWORD': 'termserver',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'CONN_MAX_AGE': 3600
    }
}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 120,
    'fanout_prefix': True,
    'fanout_patterns': True
}

REST_FRAMEWORK = {
    'DEFAULT_MODEL_SERIALIZER_CLASS':
    'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'PAGINATE_BY': 100,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 250,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': ['rest_framework.filters.DjangoFilterBackend'],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DATETIME_FORMAT': 'iso-8601',
    'DATETIME_INPUT_FORMATS': ['iso-8601'],
    'DATE_FORMAT': 'iso-8601',
    'DATE_INPUT_FORMATS': ['iso-8601']
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format':
            '%(levelname)s %(asctime)s %(module)s %(process)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'elasticsearch.trace': {
            'handlers': ['console'],
            'level': 'ERROR'
        },
        'core': {
            'handlers': ['console'],
            'level': 'DEBUG'
        }
    }
}

# The namespace for all new content created on this server
# The default is the Savannah Informatics SNOMED namespace
SNOMED_NAMESPACE_IDENTIFIER = 1000169
