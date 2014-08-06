# coding=utf-8
"""Load the most recent SNOMED UK drug release delta"""
__author__ = 'ngurenyaga'

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from .shared.discover import enumerate_release_files
from .shared.load import load_release_files, refresh_materialized_views


class Command(BaseCommand):
    """Management command to load the newest delta SNOMED UK drug release"""
    help = 'Load the newest delta ( fortnightly ) UK drug release'

    def handle(self, *args, **options):
        """The command's entry point"""
        try:
            load_release_files(enumerate_release_files("DELTA_DRUG"))
            refresh_materialized_views()
        except ValidationError as e:
            raise CommandError("Validation failure: %s" % e.message)

        self.stdout.write('Successfully loaded the latest UK drug extension delta')
