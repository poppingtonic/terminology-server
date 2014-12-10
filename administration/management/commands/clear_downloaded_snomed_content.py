# coding=utf-8
"""Get the content from a predefined Dropbox folder"""
__author__ = 'ngurenyaga'
import shutil
import logging

from django.core.management.base import BaseCommand
from .fetch_snomed_content_from_dropbox import (
    WORKING_FOLDER, EXTRACT_WORKING_FOLDER)

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """Very unsafe; to be run only to clear space on CircleCI"""
    help = 'Delete downloaded SNOMED content; *UNSAFE* - use only on CircleCI'

    def handle(self, *args, **options):
        """The command's entry point"""
        shutil.rmtree(WORKING_FOLDER, ignore_errors=False)
        shutil.rmtree(EXTRACT_WORKING_FOLDER, ignore_errors=False)
