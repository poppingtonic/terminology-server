# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    SQL = '''
CREATE OR REPLACE FUNCTION generate_subsumption_maps()
RETURNS TABLE(concept_id bigint, direct_parents bigint[], parents bigint[], direct_children bigint[], children bigint[]) AS $$
    from collections import defaultdict
    from datetime import datetime

    PARENTS_TO_CHILDREN_MAP = defaultdict(set)
    CHILDREN_TO_PARENTS_MAP = defaultdict(set)

    def get_transitive_closure_map():
        for rel in plpy.execute("SELECT source_id, destination_id FROM snomed_relationship WHERE type_id = '116680003'"):
            CHILDREN_TO_PARENTS_MAP[rel["source_id"]].add(rel["destination_id"])
            PARENTS_TO_CHILDREN_MAP[rel["destination_id"]].add(rel["source_id"])

    def walk(graph, start_node):
        """Breadth first traversal"""
        visited, queue = set(), [start_node]
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.add(vertex)
                queue.extend(graph[vertex] - visited)

        # PL/Python does not know how to map a set to a PostgreSQL array, hence the conversion to a list
        # Also, the start node should not be listed as one of its own children
        return list(visited - set([start_node]))

    def get_children_of(parent_id):
        """Return the children and descendants of a concept"""
        results = walk(PARENTS_TO_CHILDREN_MAP, parent_id)
        plpy.debug("The children of %d are %s" % (parent_id, results))
        return results

    def get_direct_children_of(parent_id):
        """Return the immediate children of a concept"""
        results = list(PARENTS_TO_CHILDREN_MAP.get(parent_id, []))
        plpy.debug("The direct children of %d are %s" % (parent_id, results))
        return results

    def get_parents_of(child_id):
        """Return the parents and ancestors of a concept"""
        results = walk(CHILDREN_TO_PARENTS_MAP, child_id)
        plpy.debug("The parents of %d are %s" % (child_id, results))
        return results

    def get_direct_parents_of(child_id):
        """Return the immediate parents of a concept"""
        results = list(CHILDREN_TO_PARENTS_MAP.get(child_id, []))
        plpy.debug("The direct parents of %d are %s" % (child_id, results))
        return results

    # Compose the return list
    RETURN_LIST = []
    get_transitive_closure_map()

    concept_count_result = plpy.execute("SELECT count(DISTINCT component_id) FROM snomed_concept")
    plpy.info(concept_count_result)
    concept_count = concept_count_result[0]["count"]
    plpy.info("%s concepts to go over" % concept_count)

    done = 1
    skipped = 1
    start_time = datetime.now()

    concepts = plpy.execute("SELECT DISTINCT component_id FROM snomed_concept")
    for concept in concepts:
        concept_id = concept["component_id"]
        if concept_id in CHILDREN_TO_PARENTS_MAP or concept_id in PARENTS_TO_CHILDREN_MAP:
            entry = [
                concept_id,
                get_direct_parents_of(concept_id),
                get_parents_of(concept_id),
                get_direct_children_of(concept_id),
                get_children_of(concept_id)
            ]
            plpy.debug("Adding '%s' to return list" % entry)
            RETURN_LIST.append(entry)

            # Timing
            done = done + 1
            seconds_spent = (datetime.now() - start_time).seconds
            if not done % 1000 and seconds_spent > 0:
                rate_per_minute = (done + skipped)* 60 / float(seconds_spent)
                minutes_left = (concept_count - done) / rate_per_minute
                param_tuple = (done, skipped, seconds_spent/60, seconds_spent % 60, rate_per_minute, minutes_left)
                plpy.debug("Done %d, skipped %d, in %d minutes %d seconds, %d/minute, remaining %d minutes" % param_tuple)
        else:
            plpy.debug("Concept '%d' [ %s ] has no entry in either subsumption map" % (concept_id, type(concept_id)))
            skipped = skipped + 1

    plpy.info("Finished generating subsumption table. Processed %d entries and skipped %d entries" % (done, skipped))

    return RETURN_LIST
$$ LANGUAGE plpythonu;

CREATE MATERIALIZED VIEW snomed_subsumption AS
SELECT concept_id, direct_parents, parents, direct_children, children FROM generate_subsumption_maps();
    '''

    dependencies = [
        ('core', '0002_auto_20140716_1216'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
