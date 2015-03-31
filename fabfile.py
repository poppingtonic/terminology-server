# coding=utf-8
"""Helpers - to reduce repetitive command line incantations"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from fabric.api import local, task  # NOQA
from django.conf import settings  # NOQA

BASE_DIR = settings.BASE_DIR


@task
def reset():
    """Drop and re-create the database"""
    sudo = 'sudo -u postgres'
    local(
        '%s psql -c "DROP DATABASE IF EXISTS %s"' %
        (sudo, settings.DATABASES['default']['NAME'])
    )
    local(
        '%s psql -c "CREATE DATABASE %s"' %
        (sudo, settings.DATABASES['default']['NAME'])
    )
    local('{}/manage.py migrate --noinput'.format(BASE_DIR))


@task
def run():
    """Run the various services that are needed"""
    local('{}/manage.py runserver'.format(BASE_DIR))
    local('{}/celery -A config worker -l info'.format(BASE_DIR))


@task
def load_snomed():
    """Helper to make this repetitive task less dreary"""
    local('{}/manage.py load_full_release'.format(BASE_DIR))


@task(default=True)
def rebuild():
    """Run this after finishing content updates"""
    local('{}/manage.py refresh_materialized_views'.format(BASE_DIR))


@task
def retrieve_terminology_data():
    """Retrieve the terminology archive and extract it"""
    local('{}/manage.py fetch_snomed_content_from_dropbox'.format(BASE_DIR))


@task
def clear_terminology_data():
    """Retrieve the terminology archive and extract it"""
    local('{}/manage.py clear_downloaded_snomed_content'.format(BASE_DIR))


@task
def build():
    """Backup, reset the database, fetch & load content, denormalize, index"""
    reset()
    retrieve_terminology_data()
    load_snomed()

    if os.getenv('CIRCLECI'):
        # We have a disk space quota on CircleCI
        clear_terminology_data()

    rebuild()