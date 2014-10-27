# coding=utf-8
"""Load the current UK full clinical release & the current drug release"""
__author__ = 'ngurenyaga'
import itertools
from collections import defaultdict
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from .shared.discover import enumerate_release_files
from .shared.load import load_release_files


class Command(BaseCommand):
    """Management command to load the newest full SNOMED UK clinical release"""
    help = 'Load the current full clinical release & drug release'

    def handle(self, *args, **options):
        """The command's entry point"""
        try:
            combined_path_dict = defaultdict(list)
            for k, v in itertools.chain(
                    enumerate_release_files("FULL_CLINICAL").iteritems(),
                    enumerate_release_files("FULL_DRUG").iteritems()):
                combined_path_dict[k] += v

            load_release_files(combined_path_dict)
        except ValidationError as e:
            raise CommandError("Validation failure: %s" % e.message)

        self.stdout.write(
            'Successfully loaded the full SNOMED clinical and drug releases')
