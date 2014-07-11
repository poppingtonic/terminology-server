# coding=utf-8
"""Load the most recent SNOMED UK drug release delta"""
__author__ = 'ngurenyaga'

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from .shared.discover import enumerate_release_files

import pprint


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
            pprint.pprint(
                {k: [path.name for path in paths] for k, paths in files.iteritems()},
                indent=2
            )
            # TODO - respect module dependencies
            # TODO - ensure that we are not skipping a delta
            pass
        except ValidationError as e:
            raise CommandError("Validation failure: %s" % e.message)

        self.stdout.write('Successfully loaded the latest UK drug extension delta')
