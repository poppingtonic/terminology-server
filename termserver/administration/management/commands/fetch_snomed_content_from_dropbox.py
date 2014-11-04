# coding=utf-8
"""Get the content from a predefined Dropbox folder"""
__author__ = 'ngurenyaga'
import dropbox

from django.core.management.base import BaseCommand

# The bulky SNOMED content is kept on DropBox ( too big for GIT )
SNOMED_FOLDER_URL = \
    'https://www.dropbox.com/sh/zxg5mkeibq2sp14/AACSO2Bc4iNyi27pxcWAwNb3a?dl=0'
DROPBOX_APP_KEY = 'fyukmm3h0a65ssv'
DROPBOX_APP_SECRET = 'oslxpyyajgcoqqi'
DROPBOX_ACCESS_TOKEN = \
    'eriIgWvfTBQAAAAAAAAHrOy2aZxAzWpeu-CI6XsmzM0zBmT5LqpdkygcLM1SIs1y'


class Command(BaseCommand):
    """The SNOMED content is too large to be distributed via GIT"""
    help = 'Fetch the current SNOMED content from Dropbox'

    def handle(self, *args, **options):
        """The command's entry point"""
        client = dropbox.client.DropboxClient(DROPBOX_ACCESS_TOKEN)

