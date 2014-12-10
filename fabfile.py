# coding=utf-8
"""Helpers - to reduce repetitive command line incantations"""
__author__ = 'ngurenyaga'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from fabric.api import local, task
from administration.management.commands.shared.load import (
    refresh_materialized_views,
    refresh_dynamic_snapshot
)
from django.conf import settings

BASE_DIR = settings.BASE_DIR


@task
def reset():
    """Drop and re-create the database"""
    sudo = 'sudo -u postgres'
    local('%s psql -c "DROP DATABASE IF EXISTS termserver"' % sudo)
    local('%s psql -c "CREATE DATABASE termserver"' % sudo)
    local('{}/manage.py clean_pyc'.format(BASE_DIR))
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
    local('{}/manage.py elasticsearch_index'.format(BASE_DIR))


@task
def backup():
    """Export all custom SIL content and also back it up online"""
    # TODO Delegate to the export API endpoint
    pass


@task
def build():
    """Backup, reset the database, fetch & load content, denormalize, index"""
    if not os.getenv('CIRCLECI'):
        # No point running this on CI; nothing to back up
        backup()

    reset()
    retrieve_terminology_data()
    load_snomed()

    if os.getenv('CIRCLECI'):
        # We have a disk space quota on CircleCI
        clear_terminology_data()

    refresh_snapshot()
    refresh_views()
    index()
    local('fab build')


@task(default=True)
def rebuild():
    """Rebuild without first droping the database"""
    backup()
    refresh_snapshot()
    refresh_views()
    index()


@task
def retrieve_terminology_data():
    """Retrieve the terminology archive and extract it"""
    local('{}/manage.py fetch_snomed_content_from_dropbox'.format(BASE_DIR))


@task
def clear_terminology_data():
    """Retrieve the terminology archive and extract it"""
    local('{}/manage.py clear_downloaded_snomed_content'.format(BASE_DIR))


@task
def test(*args, **kwargs):
    local('flake8 --exclude=migrations {}'.format(BASE_DIR))
    if os.getenv('CIRCLECI'):
        build()  # Do a fresh database and search index build if running on CI
    local("py.test --cov-report html --cov {}"
          .format(BASE_DIR))
    local("coverage report --fail-under=100")
