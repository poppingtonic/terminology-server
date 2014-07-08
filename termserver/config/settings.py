"""Terminology API server project settings"""
# -coding=utf-8
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '36o32ca(s_*hzwh5*8snp($fajwwl&j%d08^xcnes4j-0rx$#3'
DEBUG = True
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['.slade360.co.ke', '.localhost']
INSTALLED_APPS = (
    # Built in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    'django_extensions',
    # Our apps
    'core',
    'refset',
    'search',
    'authoring',
    'expression_repository',
    'administration',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
        'CONN_MAX_AGE': 300
    }
}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'

# SNOMED settings
from core.subsumption import Tester
SNOMED_TESTER = Tester()

# Test optimizations
# Use nose
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    "--with-coverage",
    "--cover-branches",
    "--cover-html",
    "--cover-html-dir=coverage_html_reports",
    "--cover-erase",
    "--cover-package=core,refset,search,authoring,administration",
    "--cover-min-percentage=100",
    "--with-xunit",
    "--with-fixture-bundling"]

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'

