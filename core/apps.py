import logging

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from psycopg2.extras import register_composite, CompositeCaster

from administration.management.commands.shared.load \
    import _acquire_psycopg2_connection

LOGGER = logging.getLogger(__name__)


class DictComposite(CompositeCaster):
    """Composite types come as dicts, not namedtuples"""
    def make(self, values):
        return dict(zip(self.attnames, values))


def setup_composites(sender, **kwargs):
    """Register type converters after migration"""
    with _acquire_psycopg2_connection() as conn:
            register_composite('denormalized_description', conn, globally=True,
                               factory=DictComposite)
            register_composite('expanded_relationship', conn, globally=True,
                               factory=DictComposite)


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = 'SNOMED Core Components'

    def ready(self):
        """Register type converters for composite types"""
        try:
            # Are we in a normal startup?
            setup_composites(self)
            LOGGER.debug(
                'Normal startup; Set up type converter for '
                'denormalized_description and expanded_relationship '
                'in the core ready()'
            )
        except:
            # We are rebuilding, migrations have not run
            post_migrate.connect(setup_composites, sender=self)
            LOGGER.debug(
                'Build; scheduled set up type converter for '
                'denormalized_description and expanded_relationship '
                'in the core ready()'
            )
