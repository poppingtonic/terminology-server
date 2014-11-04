# coding=utf-8
"""Helpers - to reduce repetitive command line incantations"""
__author__ = 'ngurenyaga'
from fabric.api import local, task
from django.conf import settings

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from administration.management.commands.shared.load import (
    refresh_materialized_views,
    refresh_dynamic_snapshot
)


@task
def reset():
    """Drop and re-create the database"""
    sudo = 'sudo -u postgres'
    local('%s psql -c "DROP DATABASE IF EXISTS termserver"' % sudo)
    local('%s psql -c "CREATE DATABASE termserver"' % sudo)
    local('{}/manage.py clean_pyc'.format(settings.BASE_DIR))
    local('{}/manage.py migrate --noinput'.format(settings.BASE_DIR))


@task
def run():
    """Run the various services that are needed"""
    local('{}/manage.py runserver'.format(settings.BASE_DIR))
    local('{}/celery -A config worker -l info'.format(settings.BASE_DIR))


@task
def load_snomed():
    """Helper to make this repetitive task less dreary"""
    local('{}/manage.py load_full_release'.format(settings.BASE_DIR))


@task
def refresh_snapshot():
    """Refresh the dynamic snapshots - necessary after a content update"""
    refresh_dynamic_snapshot()


@task
def refresh_views():
    """Refresh the materialized views - necessary after a content update"""
    refresh_materialized_views()


@task
def index():
    """Rebuild the SNOMED concept search index"""
    local('{}/manage.py elasticsearch_index'.format(settings.BASE_DIR))


@task
def backup():
    """Export all custom SIL content and also back it up online"""
    # TODO Track the export folder in GIT; it should be small enough for that
    pass


@task
def refresh():
    """Recalculate all materialized views - necessary after a content update"""
    refresh_snapshot()
    refresh_views()


@task
def reset_and_load():
    """Lazy guy's shortcut"""
    reset()
    load_snomed()
    refresh()


@task
def reset_and_load_no_refresh():
    """Was used during performance optimization"""
    reset()
    load_snomed()


@task
def build():
    """Backup, reset the database, load content, denormalize, (re)-index"""
    backup()
    reset_and_load()
    index()
    # TODO Produce a docker image


@task(default=True)
def rebuild():
    """Rebuild without first droping the database"""
    backup()
    refresh()
    index()


@task
def retrieve_terminology_data():
    """Retrieve the terminology archive and extract it"""
    # TODO - Fetch and extract the data into the correct location
    pass
