import logging

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from core.apps import setup_composites

LOGGER = logging.getLogger(__name__)


class APIConfig(AppConfig):
    name = 'api'
    verbose_name = 'SNOMED Core API'

    def ready(self):
        """Register type converters for composite types"""
        try:
            # Are we in a normal startup?
            setup_composites(self)
            LOGGER.debug(
                'Normal startup; Set up type converter for '
                'denormalized_description and expanded_relationship '
                'in the API ready()'
            )
        except:
            # We are rebuilding, migrations have not run
            post_migrate.connect(setup_composites, sender=self)
            LOGGER.debug(
                'Build; scheduled set up type converter for '
                'denormalized_description and expanded_relationship'
                'in the API ready()'
            )
