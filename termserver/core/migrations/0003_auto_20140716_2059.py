# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    SQL = '''
DROP FUNCTION IF EXISTS generate_subsumption_maps() CASCADE;
CREATE OR REPLACE FUNCTION generate_subsumption_maps() RETURNS
TABLE(
  concept_id bigint,
  is_a_direct_parents text, is_a_parents text, is_a_direct_children text, is_a_children text,
  part_of_direct_parents text, part_of_parents text, part_of_direct_children text, part_of_children text,
  other_direct_parents text, other_parents text, other_direct_children text, other_children text
) AS $$
    from collections import defaultdict
    from datetime import datetime

    import ujson as json

    IS_A_PARENTS_TO_CHILDREN_MAP = defaultdict(set)
    IS_A_CHILDREN_TO_PARENTS_MAP = defaultdict(set)

    PART_OF_PARENTS_TO_CHILDREN_MAP = defaultdict(set)
    PART_OF_CHILDREN_TO_PARENTS_MAP = defaultdict(set)

    OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_MAP = defaultdict(set)
    OTHER_RELATIONSHIPS_CHILDREN_TO_PARENTS_MAP = defaultdict(set)

    def _get_transitive_closure_map(type_id, C2P_MAP, P2C_MAP, is_inclusion_query=True):
        if is_inclusion_query:
            query = "SELECT DISTINCT(component_id), source_id, destination_id FROM snomed_relationship WHERE type_id IN (%s)" % type_id
        else:
            query = "SELECT DISTINCT(component_id), source_id, destination_id FROM snomed_relationship WHERE type_id NOT IN (%s)" % type_id
        # The contents are "stringified"
        for rel in plpy.execute(query):
            C2P_MAP[rel["source_id"]].add(
              json.dumps({
                "concept_id": rel["destination_id"],
                "relationship_id": rel["component_id"]
              })
            )
            P2C_MAP[rel["destination_id"]].add(
              json.dumps({
                "concept_id": rel["source_id"],
                "relationship_id": rel["component_id"]
              })
            )

    def get_is_a_transitive_closure_map():
        return _get_transitive_closure_map(
            '116680003', IS_A_CHILDREN_TO_PARENTS_MAP, IS_A_PARENTS_TO_CHILDREN_MAP)

    def get_part_of_transitive_closure_map():
        return _get_transitive_closure_map(
            '123005000', PART_OF_CHILDREN_TO_PARENTS_MAP, PART_OF_PARENTS_TO_CHILDREN_MAP)

    def get_other_relationships_transitive_closure_map():
        return _get_transitive_closure_map(
            '116680003,123005000', OTHER_RELATIONSHIPS_CHILDREN_TO_PARENTS_MAP, OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_MAP, is_inclusion_query=False)

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
        return json.dumps(list(visited - set([start_node])))

    # Work on the |is a| relationships
    def get_is_a_children_of(parent_id):
        return walk(IS_A_PARENTS_TO_CHILDREN_MAP, parent_id)

    def get_is_a_direct_children_of(parent_id):
        return json.dumps(list(IS_A_PARENTS_TO_CHILDREN_MAP.get(parent_id, [])))

    def get_is_a_parents_of(child_id):
        return walk(IS_A_CHILDREN_TO_PARENTS_MAP, child_id)

    def get_is_a_direct_parents_of(child_id):
        return json.dumps(list(IS_A_CHILDREN_TO_PARENTS_MAP.get(child_id, [])))

    # Work on the |part of| relationships
    def get_part_of_children_of(parent_id):
        return walk(PART_OF_PARENTS_TO_CHILDREN_MAP, parent_id)

    def get_part_of_direct_children_of(parent_id):
        return json.dumps(list(PART_OF_PARENTS_TO_CHILDREN_MAP.get(parent_id, [])))

    def get_part_of_parents_of(child_id):
        return walk(PART_OF_CHILDREN_TO_PARENTS_MAP, child_id)

    def get_part_of_direct_parents_of(child_id):
        return json.dumps(list(PART_OF_CHILDREN_TO_PARENTS_MAP.get(child_id, [])))

    # Work on the other kinds of relationships - not |is a| or |part of|
    def get_other_children_of(parent_id):
        return walk(OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_MAP, parent_id)

    def get_other_direct_children_of(parent_id):
        return json.dumps(list(OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_MAP.get(parent_id, [])))

    def get_other_parents_of(child_id):
        return walk(OTHER_RELATIONSHIPS_CHILDREN_TO_PARENTS_MAP, child_id)

    def get_other_direct_parents_of(child_id):
        return json.dumps(list(OTHER_RELATIONSHIPS_CHILDREN_TO_PARENTS_MAP.get(child_id, [])))

    # Compose the return list
    RETURN_LIST = []

    # Load the transitive closure maps into memory
    get_is_a_transitive_closure_map()
    get_part_of_transitive_closure_map()
    get_other_relationships_transitive_closure_map()

    concept_count_result = plpy.execute("SELECT count(DISTINCT component_id) FROM snomed_concept")
    concept_count = concept_count_result[0]["count"]
    plpy.info("%s concepts to go over" % concept_count)

    done = 1
    start_time = datetime.now()
    for concept in plpy.execute("SELECT DISTINCT component_id FROM snomed_concept"):
        concept_id = concept["component_id"]
        RETURN_LIST.append((
            concept_id,
            get_is_a_direct_parents_of(concept_id),
            get_is_a_parents_of(concept_id),
            get_is_a_direct_children_of(concept_id),
            get_is_a_children_of(concept_id),
            get_part_of_direct_parents_of(concept_id),
            get_part_of_parents_of(concept_id),
            get_part_of_direct_children_of(concept_id),
            get_part_of_children_of(concept_id),
            get_other_direct_parents_of(concept_id),
            get_other_parents_of(concept_id),
            get_other_direct_children_of(concept_id),
            get_other_children_of(concept_id),
        ))

        # Timing
        done = done + 1
        if not done % 30000:
            seconds_spent = (datetime.now() - start_time).total_seconds()
            rate_per_minute = done* 60 / float(seconds_spent)
            minutes_left = (concept_count - done) / rate_per_minute
            param_tuple = (done, seconds_spent/60, seconds_spent % 60, rate_per_minute, minutes_left)
            plpy.info("Done %d in %d minutes %d seconds, %d/minute, remaining %d minutes" % param_tuple)

    plpy.info("Finished generating subsumption table. Processed %d entries;" % done)
    return RETURN_LIST
$$ LANGUAGE plpythonu;

CREATE MATERIALIZED VIEW snomed_subsumption AS
SELECT
  concept_id,
  is_a_direct_parents, is_a_parents, is_a_direct_children, is_a_children,
  part_of_direct_parents, part_of_parents, part_of_direct_children, part_of_children,
  other_direct_parents, other_parents, other_direct_children, other_children
FROM generate_subsumption_maps();
CREATE INDEX snomed_subsumption_concept_id ON snomed_subsumption(concept_id);
    '''

    dependencies = [
        ('core', '0002_auto_20140716_1216'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
