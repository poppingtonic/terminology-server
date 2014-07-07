# -coding=utf-8
__author__ = 'ngurenyaga'
"""
This module implements SNOMED subsumption testing ( using an in-memory map ).
This map is non-persistent and may therefore be re-created on every app server start.

The structure of the lookup map is as follows:
    Key: subtype
    Value: set of ids of DIRECT parents

For the data that we get back from the query below:
    destination_id is the parent
    source_id is the subtype
"""

from django.conf import settings
from django.db import connection
from django.core import management

import sys
import logging

LOGGER = logging.getLogger(__name__)


class Tester(object):
    """The actual subsumption tester"""
    def __init__(self):
        """
        The query below relies on the immutability of SNOMED IDs
        """
        self.CHILDEN_TO_PARENTS_MAP = {}
        self.PARENTS_TO_CHILDREN_MAP = {}
        self.CHILDREN_TO_PARENTS_KEY = "children_to_parents_map"
        self.PARENTS_TO_CHILDREN_KEY = "parents_to_children_map"
        self.snapshot_loaded = False
        self.setup_done = False

    def _do_setup(self):
        # SQLite has no boolean data type
        self.db_settings = settings.DATABASES["default"]
        if self.db_settings["ENGINE"] == "django.db.backends.sqlite3":
            self.IS_A_RELATIONSHIPS_QUERY = """
                    SELECT source_id, destination_id FROM snomed_relationship
                    WHERE active = 1 AND relationship_type_id = '116680003'
                """
        else:
            self.IS_A_RELATIONSHIPS_QUERY = """
                    SELECT source_id, destination_id FROM snomed_relationship
                    WHERE active = True AND relationship_type_id = '116680003'
                """
        if not self.setup_done:
            self.setup()

    def setup(self):
        def _concepts_exist():
            cur = connection.cursor()
            connection.cursor().execute("SELECT count(*) FROM snomed_concept")
            resp = cur.fetchall()
            return resp and resp[0] and resp[0][0] and int(resp[0][0]) > 0

        if not self.setup_done:
            # Special case for tests; bearable since we are in-memory anyway
            # Must be called only once
            # Pass "-a '!needs_snomed'" to test arguments
            if 'test' in sys.argv and not self.snapshot_loaded and not _concepts_exist() \
                    and not '!needs_snomed' in sys.argv and not "--attr=!needs_snomed" in sys.argv:
                management.call_command('load_snomed_us_snapshot')
                self.snapshot_loaded = True
                LOGGER.debug('Loading SNOMED. sys.argv is "%s"' %
                             str(sys.argv))
            else:
                LOGGER.error(
                    'Not loading SNOMED. sys.argv is "%s"' % str(sys.argv))

            # The actual load
            if not len(self.CHILDEN_TO_PARENTS_MAP) and not len(self.PARENTS_TO_CHILDREN_MAP):
                # Will be lazily initialized
                self.CHILDREN_TO_PARENTS_MAP, self.PARENTS_TO_CHILDREN_MAP = self.get_transitive_closure_map(
                )
                # Will be used to cache trees that have been "seen" and
                # computed
                self.ALL_PARENTS_CACHE = {}
                self.ALL_CHILDREN_CACHE = {}

            # Don't repeat setup
            self.setup_done = True

    def get_transitive_closure_map(self):
        cur = connection.cursor()
        cur.execute(self.IS_A_RELATIONSHIPS_QUERY)
        for (source_id, destination_id) in cur.fetchall():
            # Populate the children to parents map
            if source_id in self.CHILDEN_TO_PARENTS_MAP:
                if destination_id not in self.CHILDEN_TO_PARENTS_MAP[source_id]:
                    self.CHILDEN_TO_PARENTS_MAP[
                        source_id].append(destination_id)
            else:
                self.CHILDEN_TO_PARENTS_MAP[source_id] = [destination_id]

            # Populate the parents to children map
            if destination_id in self.PARENTS_TO_CHILDREN_MAP:
                if source_id not in self.PARENTS_TO_CHILDREN_MAP[destination_id]:
                    self.PARENTS_TO_CHILDREN_MAP[
                        destination_id].append(source_id)
            else:
                self.PARENTS_TO_CHILDREN_MAP[destination_id] = [source_id]

        return self.CHILDEN_TO_PARENTS_MAP, self.PARENTS_TO_CHILDREN_MAP

    def get_children_of(self, parent_id):
        self._do_setup()
        output = []

        def _walk(current_child_id):
            children = self.PARENTS_TO_CHILDREN_MAP.get(current_child_id, [])
            output.extend(children)
            for next_parent_id in children:
                _walk(next_parent_id)
            return output

        return set(_walk(parent_id))

    def get_direct_children_of(self, parent_id):
        self._do_setup()
        return self.PARENTS_TO_CHILDREN_MAP.get(parent_id, [])

    def get_parents_of(self, child_id):
        self._do_setup()
        output = []

        def _walk(current_child_id):
            parents = self.CHILDEN_TO_PARENTS_MAP.get(current_child_id, [])
            output.extend(parents)
            for next_child_id in parents:
                _walk(next_child_id)
            return output

        return _walk(child_id)

    def get_direct_parents_of(self, child_id):
        self._do_setup()
        return self.CHILDEN_TO_PARENTS_MAP.get(child_id, [])

    def is_parent_of(self, child_id, candidate_parent_id):
        """
        Return True if the SNOMED concept identified by candidate_parent_id
        is a direct or indirect parent of the one identified by child_id.
        Parents that are seen often are cached.
        """
        self._do_setup()
        if child_id in self.ALL_PARENTS_CACHE:
            parents = self.ALL_PARENTS_CACHE[child_id]
        else:
            parents = self.get_parents_of(child_id)
            self.ALL_PARENTS_CACHE[child_id] = parents
        return candidate_parent_id in parents

    def is_direct_parent_of(self, child_id, candidate_parent_id):
        """
        Return True if the SNOMED concept identified by candidate_parent_id
        is a direct parent of the one identified by child_id
        """
        self._do_setup()
        return candidate_parent_id in self.get_direct_parents_of(child_id)

    def is_child_of(self, parent_id, candidate_child_id):
        """
        Return True if the SNOMED concept identified by candidate_child_id
        is a direct or indirect child of the one identified by parent_id
        """
        self._do_setup()
        if parent_id in self.ALL_CHILDREN_CACHE:
            children = self.ALL_CHILDREN_CACHE[parent_id]
        else:
            children = self.get_children_of(parent_id)
            self.ALL_CHILDREN_CACHE[parent_id] = children
        return candidate_child_id in children

    def is_direct_child_of(self, parent_id, candidate_child_id):
        """
        Return True if the SNOMED concept identified by candidate_child_id
        is a direct child of the one identified by parent_id
        """
        self._do_setup()
        return candidate_child_id in self.get_direct_children_of(parent_id)
