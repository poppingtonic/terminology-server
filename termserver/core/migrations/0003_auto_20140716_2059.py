# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    SQL = '''
CREATE INDEX concept_component_id_index ON snomed_concept(component_id);
CREATE INDEX description_component_id_index ON snomed_description(component_id);
CREATE index source_id_index ON snomed_relationship(source_id);
CREATE index destination_id_index ON snomed_relationship(destination_id);

DROP FUNCTION generate_subsumption_maps() CASCADE;
CREATE OR REPLACE FUNCTION generate_subsumption_maps()
RETURNS TABLE(
  concept_id bigint, direct_parents bigint[], parents bigint[], direct_children bigint[], children bigint[],
  incoming_part_of_relationships bigint[], outgoing_part_of_relationships bigint[], other_incoming_relationships bigint[], other_outgoing_relationships bigint[]
) AS $$
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

    def get_incoming_part_of_relationships(concept_id):
        """Return the concepts that this is a part of"""
        query = "SELECT source_id FROM snomed_relationship WHERE type_id = 123005000 AND destination_id = %s"
        return [rel["source_id"] for rel in plpy.execute(query % concept_id)]

    def get_outgoing_part_of_relationships(concept_id):
        """Return the concepts that this is a part of"""
        query = "SELECT destination_id FROM snomed_relationship WHERE type_id = 123005000 AND source_id = %s"
        return [rel["destination_id"] for rel in plpy.execute(query % concept_id)]

    def get_other_incoming_relationships(concept_id):
        """All incoming relationships of types other than |part of| and |is a|"""
        query = "SELECT source_id FROM snomed_relationship WHERE type_id not in (116680003, 123005000) AND destination_id = %s"
        return [rel["source_id"] for rel in plpy.execute(query % concept_id)]

    def get_other_outgoing_relationships(concept_id):
        """All outgoing relationships of types other than |part of| and |is a|"""
        query = "SELECT destination_id FROM snomed_relationship WHERE type_id not in (116680003, 123005000) AND source_id = %s"
        return [rel["destination_id"] for rel in plpy.execute(query % concept_id)]

    # Compose the return list
    RETURN_LIST = []
    get_transitive_closure_map()

    concept_count_result = plpy.execute("SELECT count(DISTINCT component_id) FROM snomed_concept")
    concept_count = concept_count_result[0]["count"]
    plpy.info("%s concepts to go over" % concept_count)

    done = 1
    start_time = datetime.now()
    for concept in plpy.execute("SELECT DISTINCT component_id FROM snomed_concept"):
        concept_id = concept["component_id"]
        entry = [
            concept_id,
            get_direct_parents_of(concept_id),
            get_parents_of(concept_id),
            get_direct_children_of(concept_id),
            get_children_of(concept_id),
            get_incoming_part_of_relationships(concept_id),
            get_outgoing_part_of_relationships(concept_id),
            get_other_incoming_relationships(concept_id),
            get_other_outgoing_relationships(concept_id)
        ]
        plpy.debug("Adding '%s' to return list" % entry)
        RETURN_LIST.append(entry)

        # Timing
        done = done + 1
        seconds_spent = (datetime.now() - start_time).seconds
        if not done % 1000 and seconds_spent > 0:
            rate_per_minute = done* 60 / float(seconds_spent)
            minutes_left = (concept_count - done) / rate_per_minute
            param_tuple = (done, seconds_spent/60, seconds_spent % 60, rate_per_minute, minutes_left)
            plpy.info("Done %d in %d minutes %d seconds, %d/minute, remaining %d minutes" % param_tuple)

    plpy.info("Finished generating subsumption table. Processed %d entries" % done)

    return RETURN_LIST
$$ LANGUAGE plpythonu;

CREATE MATERIALIZED VIEW snomed_subsumption AS
SELECT
  concept_id, direct_parents, parents, direct_children, children,
  incoming_part_of_relationships, outgoing_part_of_relationships, other_incoming_relationships, other_outgoing_relationships
FROM generate_subsumption_maps();
CREATE INDEX snomed_subsumption_concept_id ON snomed_subsumption(concept_id);
    '''

    dependencies = [
        ('core', '0002_auto_20140716_1216'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
