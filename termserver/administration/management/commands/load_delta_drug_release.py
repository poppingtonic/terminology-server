# coding=utf-8
"""Load the most recent SNOMED UK drug release delta"""
__author__ = 'ngurenyaga'

from django.core.management.base import BaseCommand, CommandError
from .shared.discover import enumerate_release_files


class Command(BaseCommand):
    """Management command to load the newest delta SNOMED UK drug release"""
    help = 'Load the newest delta ( fortnightly ) UK drug release'

    def add_arguments(self, parser):
        """Set the applicable command line arguments

        :param parser:
        """
        # parser.add_argument('poll_id', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        """The command's entry point"""
        try:
            # TODO - do the actual loading ( delegate to helpers )
            files = enumerate_release_files("DELTA_DRUG")
            # TODO - respect module dependencies
            # TODO - ensure that we are not skipping a delta
            pass
        except:
            # TODO - catch more specific exceptions
            # TODO - return informative and specific error messages below
            raise CommandError('Show a specific message here')

        # TODO - write sensible feedback to standard out
        self.stdout.write('Give user feedback here')
