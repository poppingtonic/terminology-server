# coding=utf-8
"""Load the current UK full clinical release & the current drug release"""
__author__ = 'ngurenyaga'
from django.core.management.base import BaseCommand, CommandError
from .shared.discover import enumerate_release_files
from .shared.load import load_release_files


class Command(BaseCommand):
    """Management command to load the newest full SNOMED UK clinical release"""
    help = 'Load the current full clinical release & drug release'

    def handle(self, *args, **options):
        """The command's entry point"""
        try:
            load_release_files(enumerate_release_files())
            self.stdout.write(
                'Successfully loaded the full SNOMED UK '
                'clinical and drug releases')
        except Exception as e:  # Intentionally catching the base exception
            raise CommandError("Unable to load SNOMED content: %s" % e.message)
