# coding=utf-8
"""Load the current UK full clinical release & the current drug release"""
import logging

from django.core.management.base import BaseCommand, CommandError
from .shared.load import refresh_materialized_views


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command to rebuild the materialized views"""
    help = 'Refresh the materialized views ( "build" )'

    def handle(self, *args, **options):
        """The command's entry point"""
        try:
            refresh_materialized_views()
            self.stdout.write(
                'Successfully refreshed the materialized views')
        except Exception as e:  # Intentionally catching the base exception
            raise CommandError("Unable to refresh materialized views: %s" % e.message)
