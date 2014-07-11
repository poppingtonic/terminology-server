# coding=utf-8
"""Helpers - to reduce repetitive command line incantations"""
__author__ = 'ngurenyaga'
from os.path import dirname, abspath
from fabric.api import local

BASE_DIR = dirname(abspath(__file__))


def reset():
    """Spare the developer the dance of logging in as Postgres, dropping, creating, migrating etc"""
    sudo = 'sudo -u postgres'
    local('%s psql -c "DROP DATABASE IF EXISTS termserver"' % sudo)
    local('%s psql -c "CREATE DATABASE termserver"' % sudo)
    local('{}/manage.py clean_pyc'.format(BASE_DIR))
    local('{}/manage.py migrate --noinput'.format(BASE_DIR))


def run():
    """Set up everything that needs to run e.g celery, celery beat, the Django application"""
    local('{}/manage.py runserver'.format(BASE_DIR))
    # local('{}/manage.py migrate --noinput'.format(BASE_DIR))


def test():
    """A wrapper around the test invocation"""
    pass
