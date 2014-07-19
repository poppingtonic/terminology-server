# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

SQL = """
DROP FUNCTION generate_denormalized_concept_view() CASCADE;
CREATE OR REPLACE FUNCTION generate_denormalized_concept_view() RETURNS TABLE(
    concept_id bigint, effective_time date, active boolean, module_id bigint, definition_status_id bigint,
    module_name text, definition_status_name text, is_primitive boolean, is_navigation_concept boolean,
    fully_specified_name text, preferred_term text, definition text,
    descriptions text, preferred_terms text, synonyms text,
    other_outgoing_relationships text, other_incoming_relationships text,
    parents text, children text, ancestors text, descendants text, incoming_part_of text, outgoing_part_of text)
AS $$
    # HERE BE DRAGONS! The first iteration of this stored procedure needed > 20GB RAM
    # If you see "interesting" things being done here, do not rush to change them before you ask why they are there!

    from collections import defaultdict
    from datetime import datetime

    import json

    CONCEPT_QUERY = """
    SELECT
      DISTINCT(component_id) as concept_id, effective_time, active, module_id, definition_status_id,
      CASE WHEN definition_status_id = 900000000000074008 THEN true ELSE false END AS is_primitive,
      CASE WHEN component_id IN
        (SELECT UNNEST(children) AS child FROM snomed_subsumption WHERE concept_id = 363743006)
        THEN true
        ELSE false
      END as is_navigational_concept
    FROM snomed_concept
    """;

    # The concept list that is originally fetched is progressively augmented then returned
    plpy.info("About to compose concepts dict...")
    CONCEPTS = { concept["concept_id"]: defaultdict(list, concept) for concept in plpy.execute(CONCEPT_QUERY)}
    CONCEPT_COUNT = len(CONCEPTS)
    plpy.info("Finished composing concepts dict, has %d entries" % len(CONCEPTS))

    def populate_descriptions():
        """Do this as the second pass; fill in all the description related fields

        The UK reference set's id is 999001251000000103 . It takes precedence over other language reference sets
        """
        def _lookup_language_code(lang_code):
            """English only for now"""
            if lang_code == "en":
                return "English"
            else:
                raise Exception("Unknown language code '%s'" % lang_code)

        def _compose_rel(concept_row, rel_id):
            # TODO Pipe in a link to the relationship itself
            return json.dumps({
                "concept_id": rel_id,
                "name": CONCEPTS[rel_id]["preferred_term"]
            })

        plpy.info("Starting to put together the descriptions...")
        START_TIME = datetime.now()
        descr_cursor = plpy.cursor(
          """
          SELECT
            con.component_id AS concept_id, des.component_id AS description_id, des.module_id, des.type_id, des.effective_time,
            des.case_significance_id, des.term, des.language_code, des.active, ref.acceptability_id, ref.refset_id
          FROM snomed_concept con
          LEFT JOIN snomed_description des ON des.concept_id = con.component_id
          LEFT JOIN snomed_language_reference_set ref ON ref.referenced_component_id = des.component_id
          """
        )
        plpy.info("Created the concepts-descriptions join cursor, now starting the first pass...")

        # First pass, fill in the "obvious" details
        loop_count = 1
        while True:
            desc_rows = descr_cursor.fetch(1000)
            if not desc_rows:
                FIRST_LOOP_FINISH_TIME = datetime.now()
                break
            for desc_row in desc_rows:
                # Get hold of a concept row
                concept_row = CONCEPTS[desc_row["concept_id"]]
                descr = json.dumps({
                    "id": desc_row["description_id"],
                    "module_id": desc_row["module_id"],
                    "effective_time": desc_row["effective_time"],
                    "language_code": desc_row["language_code"],
                    "language_name": _lookup_language_code(desc_row["language_code"]),
                    "active": desc_row["active"],
                    "type_id": desc_row["type_id"],
                    "term": desc_row["term"],
                    "case_significance_id": desc_row["case_significance_id"]
                })
                concept_row["descriptions"].append(descr)

                # Definitions, FSN and synonyms
                if desc_row["type_id"] == 900000000000550004:
                    concept_row["definition"] = desc_row["term"]
                elif desc_row["type_id"] == 900000000000003001:
                    concept_row["fully_specified_name"] = desc_row["term"]
                elif desc_row["type_id"] == 900000000000013009:
                    concept_row["synonyms"].append(descr)
                else:
                    raise Exception("Encountered unknown type id: %d" % desc_row["type_id"])

                # Preferred terms, and main preferred term
                if desc_row["acceptability_id"] == 900000000000548007:
                    # Add to list of preferred terms
                    concept_row["preferred_terms"].append(descr)

                    # Choose the single "most preferred" term
                    if not concept_row["preferred_term"]:
                        concept_row["preferred_term"] = desc_row["term"]
                    else:
                        if desc_row["refset_id"] == 999001251000000103:
                            # The UK Language reference set takes precedence over other reference sets
                            concept_row["preferred_term"] = desc_row["term"]
                elif desc_row["acceptability_id"] == 900000000000549004 or desc_row["acceptability_id"] is None:
                    if descr not in concept_row["synonyms"]:
                        concept_row["synonyms"].append(descr)
                else:
                    raise Exception("Unknown acceptability id")

            loop_count +=1
            minutes = float((datetime.now() - START_TIME).total_seconds()) / 60
            rate_per_minute = (loop_count * 1000) / minutes
            plpy.notice("Processed %s description join records; taken %s minutes; %s/min" % (loop_count * 1000, minutes, rate_per_minute))

        # Now, fill in the details that can only be filled in on second pass
        plpy.info("Finished descriptions first pass, about to start second pass")
        done = 1
        for concept_row in CONCEPTS.values():
            # Fill in some denormalized concept details
            concept_row["module_name"] = CONCEPTS[concept_row["module_id"]]["preferred_term"]
            concept_row["definition_status_name"] = CONCEPTS[concept_row["definition_status_id"]]["preferred_term"]

            # Fill in some more denormalized details within the descriptions themselves
            for descr in concept_row["descriptions"] + concept_row["preferred_terms"] + concept_row["synonyms"]:
                # Manipulate the JSON
                description = json.loads(descr)
                description["module_name"] = CONCEPTS[description["module_id"]]["preferred_term"]
                description["type_name"] = CONCEPTS[description["type_id"]]["preferred_term"]
                description["case_significance_name"] = CONCEPTS[description["case_significance_id"]]["preferred_term"]
                concept_row["descriptions"] = json.dumps(descr)

            # Failsafes
            if not concept_row["preferred_terms"]:
                raise Exception("Concept %s has no preferred terms" % concept_row["concept_id"])

            # Timing
            done = done + 1
            seconds_spent = (datetime.now() - FIRST_LOOP_FINISH_TIME).total_seconds()
            if not done % 1000 and seconds_spent > 0:
                rate_per_minute = (done * 60) / float(seconds_spent)
                param_tuple = (done, seconds_spent/60, rate_per_minute)
                plpy.info("Second pass - done %s in %s minutes, %s/minute" % param_tuple)

    def populate_relationships():
        """Fill in all relationship related fields"""
        def _compose_rel(concept_row, rel_id):
            # TODO Pipe in a link to the relationship itself
            return json.dumps({
                "concept_id": rel_id,
                "name": CONCEPTS[rel_id]["preferred_term"]
            })

        plpy.info("Starting to put together the relationships...")
        REL_START_TIME = datetime.now()
        done = 1
        for concept_row in CONCEPTS.values():
            # Get the ids of the relationships
            rel_subsumption_result = plpy.execute(
              """
              SELECT
                direct_parents, parents, direct_children, children,
                incoming_part_of_relationships, outgoing_part_of_relationships, other_incoming_relationships, other_outgoing_relationships
              FROM snomed_subsumption WHERE concept_id = %s
              """ % concept_row["concept_id"]
            )[0]
            for parent_id in rel_subsumption_result["direct_parents"]:
                concept_row["parents"].append(_compose_rel(concept_row, parent_id))

            for child_id in rel_subsumption_result["direct_children"]:
                concept_row["children"].append(_compose_rel(concept_row, child_id))

            for ancestor_id in rel_subsumption_result["parents"]:
                concept_row["ancestors"].append(_compose_rel(concept_row, ancestor_id))

            for descendant_id in rel_subsumption_result["children"]:
                concept_row["descendants"].append(_compose_rel(concept_row, descendant_id))

            for incoming_part_of_rel_id in rel_subsumption_result["incoming_part_of_relationships"]:
                concept_row["incoming_part_of"].append(_compose_rel(concept_row, incoming_part_of_rel_id))

            for outgoing_part_of_rel_id in rel_subsumption_result["outgoing_part_of_relationships"]:
                concept_row["outgoing_part_of"].append(_compose_rel(concept_row, outgoing_part_of_rel_id))

            for other_incoming_rel_id in rel_subsumption_result["other_incoming_relationships"]:
                concept_row["other_incoming_relationships"].append(_compose_rel(concept_row, other_incoming_rel_id))

            for other_outgoing_rel_id in rel_subsumption_result["other_outgoing_relationships"]:
                concept_row["other_outgoing_relationships"].append(_compose_rel(concept_row, other_outgoing_rel_id))

            # Timing
            done = done + 1
            seconds_spent = (datetime.now() - REL_START_TIME).total_seconds()
            if not done % 1000 and seconds_spent > 0:
                rate_per_minute = (done * 60) / float(seconds_spent)
                param_tuple = (done, seconds_spent/60, rate_per_minute)
                plpy.info("Relationships pass - done %s in %s minutes, %s/minute" % param_tuple)

    # Put the operations together
    populate_descriptions()
    populate_relationships()

    plpy.notice("Finished computations, about to return the results...")
    # TODO In addition to returning tuples, consider using a generator for this
    return CONCEPTS.values()
$$ LANGUAGE plpythonu;

CREATE MATERIALIZED VIEW snomed_denormalized_concept_view AS
SELECT
  concept_id, effective_time, active, module_id, definition_status_id, is_primitive, is_navigation_concept,
  descriptions, preferred_terms, synonyms, fully_specified_name, preferred_term, definition, module_name, definition_status_name,
  other_outgoing_relationships, other_incoming_relationships, parents, children, ancestors, descendants, incoming_part_of, outgoing_part_of
FROM generate_denormalized_concept_view();

"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20140716_2059'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
