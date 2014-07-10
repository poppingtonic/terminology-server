# coding=utf-8
"""Load the most recent SNOMED UK full clinical release"""
__author__ = 'ngurenyaga'

from django.core.management.base import BaseCommand, CommandError
from .shared.discover import enumerate_release_files

import pprint
import traceback


class Command(BaseCommand):
    """Management command to load the newest full SNOMED UK clinical release"""
    help = 'Load the newest full ( bi-annual ) clinical release'

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
            files = enumerate_release_files("FULL_CLINICAL")
            pprint.pprint(dict(files), self.stdout, indent=2)
            # TODO - respect module dependencies
            pass
        except:
            # TODO - catch more specific exceptions
            # TODO - return informative and specific error messages below
            traceback.print_exc()
            raise CommandError('Show a specific message here')

        # TODO - write sensible feedback to standard out
        self.stdout.write('Give user feedback here')
