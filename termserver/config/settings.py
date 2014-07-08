"""Terminology API server project settings"""
# -coding=utf-8
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '36o32ca(s_*hzwh5*8snp($fajwwl&j%d08^xcnes4j-0rx$#3'
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []
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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'

# SNOMED settings
from core.subsumption import Tester
SNOMED_TESTER = Tester()
