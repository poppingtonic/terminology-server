# coding=utf-8
"""Load the most recent SNOMED UK full clinical release"""
__author__ = 'ngurenyaga'

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from .shared.discover import enumerate_release_files
from .shared.load import load_release_files


class Command(BaseCommand):
    """Management command to load the newest full SNOMED UK clinical release"""
    help = 'Load the newest full ( bi-annual ) clinical release'

    def handle(self, *args, **options):
        """The command's entry point"""
        try:
            load_release_files(enumerate_release_files("FULL_CLINICAL"))
        except ValidationError as e:
            raise CommandError("Validation failure: %s" % e.message)

        self.stdout.write(
            'Successfully loaded the full SNOMED clinical release')
