# -coding=utf-8
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
__author__ = 'ngurenyaga'

from django.db import connection

import logging

LOGGER = logging.getLogger(__name__)


class Tester(object):
    """The actual subsumption tester"""
    def __init__(self):
        """
        The query below relies on the immutability of SNOMED IDs
        """
        self.CHILDREN_TO_PARENTS_MAP = {}  # children to parents map
        self.PARENTS_TO_CHILDREN_MAP = {}  # Parents to children map
        self.CHILDREN_TO_PARENTS_KEY = "children_to_parents_map"
        self.PARENTS_TO_CHILDREN_KEY = "parents_to_children_map"

        # Needed so as to avoid double initialization
        self.snapshot_loaded = False
        self.setup_done = False

        # Will be used to cache trees that have been "seen" and computed
        self.ALL_PARENTS_CACHE = {}
        self.ALL_CHILDREN_CACHE = {}

        # Predefined queries
        # TODO - Use a materialized view here
        self.IS_A_RELATIONSHIPS_QUERY = """
          SELECT source_id, destination_id FROM snomed_relationship
          WHERE active = True AND relationship_type_id = '116680003'
        """

    def setup(self):
        """The actual data load"""
        if not self.setup_done:
            # The actual transitive map computation
            if not len(self.CHILDREN_TO_PARENTS_MAP) and not len(self.PARENTS_TO_CHILDREN_MAP):
                self.CHILDREN_TO_PARENTS_MAP, self.PARENTS_TO_CHILDREN_MAP = self.get_transitive_closure_map()

            # Don't repeat setup
            self.setup_done = True

    def get_transitive_closure_map(self):
        """Generate the in-memory maps that will be used to test for subsumption"""
        cur = connection.cursor()
        cur.execute(self.IS_A_RELATIONSHIPS_QUERY)
        for (source_id, destination_id) in cur.fetchall():
            # Populate the children to parents map
            if source_id in self.CHILDREN_TO_PARENTS_MAP:
                if destination_id not in self.CHILDREN_TO_PARENTS_MAP[source_id]:
                    self.CHILDREN_TO_PARENTS_MAP[
                        source_id].append(destination_id)
            else:
                self.CHILDREN_TO_PARENTS_MAP[source_id] = [destination_id]

            # Populate the parents to children map
            if destination_id in self.PARENTS_TO_CHILDREN_MAP:
                if source_id not in self.PARENTS_TO_CHILDREN_MAP[destination_id]:
                    self.PARENTS_TO_CHILDREN_MAP[
                        destination_id].append(source_id)
            else:
                self.PARENTS_TO_CHILDREN_MAP[destination_id] = [source_id]

        return self.CHILDREN_TO_PARENTS_MAP, self.PARENTS_TO_CHILDREN_MAP

    def get_children_of(self, parent_id):
        """Return the children and descendants of a concept

        :param parent_id:
        """
        self.setup()
        output = []

        def _walk(current_child_id):
            children = self.PARENTS_TO_CHILDREN_MAP.get(current_child_id, [])
            output.extend(children)
            for next_parent_id in children:
                _walk(next_parent_id)
            return output

        return set(_walk(parent_id))

    def get_direct_children_of(self, parent_id):
        """Return the immediate children of a concept

        :param parent_id:
        """
        self.setup()
        return self.PARENTS_TO_CHILDREN_MAP.get(parent_id, [])

    def get_parents_of(self, child_id):
        """Return the parents and ancestors of a concept

        :param child_id:
        """
        self.setup()
        output = []

        def _walk(current_child_id):
            parents = self.CHILDREN_TO_PARENTS_MAP.get(current_child_id, [])
            output.extend(parents)
            for next_child_id in parents:
                _walk(next_child_id)
            return output

        return _walk(child_id)

    def get_direct_parents_of(self, child_id):
        """Return the immediate parents of a concept

        :param child_id:
        """
        self.setup()
        return self.CHILDREN_TO_PARENTS_MAP.get(child_id, [])

    def is_parent_of(self, child_id, candidate_parent_id):
        """
        Return True if the SNOMED concept identified by candidate_parent_id
        is a direct or indirect parent of the one identified by child_id.
        Parents that are seen often are cached.

        :param child_id:
        :param candidate_parent_id:
        """
        self.setup()
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

        :param child_id:
        :param candidate_parent_id:
        """
        self.setup()
        return candidate_parent_id in self.get_direct_parents_of(child_id)

    def is_child_of(self, parent_id, candidate_child_id):
        """
        Return True if the SNOMED concept identified by candidate_child_id
        is a direct or indirect child of the one identified by parent_id

        :param parent_id:
        :param candidate_child_id:
        """
        self.setup()
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

        :param parent_id:
        :param candidate_child_id:
        """
        self.setup()
        return candidate_child_id in self.get_direct_children_of(parent_id)
