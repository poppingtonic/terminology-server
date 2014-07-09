# coding=utf-8
"""Load the most recent SNOMED UK clinical release delta"""
__author__ = 'ngurenyaga'

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Management command to load the newest delta SNOMED UK clinical release"""
    help = 'Load the newest delta ( bi-annual ) clinical release'
    # TODO - Deltas load via the same mechanism ( because of the append only nature )
    # TODO - FKs to Concept are a BAD idea ( because the FK may refer to an older record )

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
            pass
        except:
            # TODO - catch more specific exceptions
            # TODO - return informative and specific error messages below
            raise CommandError('Show a specific message here')

        # TODO - write sensible feedback to standard out
        self.stdout.write('Give user feedback here')
