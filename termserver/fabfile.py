# coding=utf-8
"""Helpers - to reduce repetitive command line incantations"""
__author__ = 'ngurenyaga'
from fabric.api import local, task
from django.conf import settings

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
BASE_DIR = settings.BASE_DIR

from administration.management.commands.shared.load import refresh_materialized_views


@task
def reset():
    """Spare the developer the dance of logging in as Postgres, dropping, creating, migrating etc"""
    sudo = 'sudo -u postgres'
    local('%s psql -c "DROP DATABASE IF EXISTS termserver"' % sudo)
    local('%s psql -c "CREATE DATABASE termserver"' % sudo)
    local('{}/manage.py clean_pyc'.format(BASE_DIR))
    local('{}/manage.py migrate --noinput'.format(BASE_DIR))


@task
def run():
    """Set up everything that needs to run e.g celery, celery beat, the Django application"""
    local('{}/manage.py runserver'.format(BASE_DIR))
    local('{}/celery -A config worker -l info'.format(BASE_DIR))


@task
def load_snomed():
    """Helper to make this repetitive task less dreary"""
    local('{}/manage.py load_full_release'.format(BASE_DIR))


@task
def refresh_views():
    """Refresh all the materialized views - usually necessary after a content update"""
    refresh_materialized_views()


@task
def index():
    """Rebuild the SNOMED concept search index"""
    local('{}/manage.py elasticsearch_index'.format(BASE_DIR))


@task
def backup():
    """Export all custom SIL refset content to the data directory and also back it up online"""
    pass


@task
def reset_and_load():
    """Lazy guy's shortcut"""
    reset()
    load_snomed()


@task(default=True)
def build():
    """Reset the database, load content, pre-compute materialized views, rebuild search index"""
    backup()
    refresh_views()
    reset_and_load()
    index()


@task
def retrieve_terminology_data():
    """Retrieve the terminology archive ( initial revision ) from Google Drive and extract it"""
    # TODO - Fetch and extract the data into the correct location
    pass
