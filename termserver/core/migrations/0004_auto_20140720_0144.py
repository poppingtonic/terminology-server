# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

SQL = """
-- We need this custom type so that we can aggregate all the information that relates to one description together
DROP TYPE description CASCADE;
CREATE TYPE description AS (
    component_id bigint,
    module_id bigint,
    type_id bigint,
    effective_time date,
    case_significance_id bigint,
    term text,
    language_code character varying(2),
    active boolean,
    acceptability_id bigint,
    refset_id bigint
);

-- The preferred term is - by a wide margin - the most queried concept attribute
CREATE OR REPLACE FUNCTION get_preferred_term(descs json[]) RETURNS text AS $$
import ujson as json

preferred_term = None

# key "f1" is the term, key "f2" is the acceptability_id, key "f3" is the refset_id
for descr in descs:
    desc_row = json.loads(descr)
    # Record the first preferred term that we see
    if desc_row["acceptability_id"] == 900000000000548007 and not preferred_term:
        preferred_term = desc_row["term"]
    # The UK Language reference set takes precedence over other reference sets and can overwrite prior values
    if desc_row["acceptability_id"] == 900000000000548007 and desc_row["refset_id"] == 999001251000000103:
        preferred_term = desc_row["term"]

# We should have found a preferred term by now ( every concept should have one )
if not preferred_term:
   raise Exception("Preferred term not found in: %s" % descs)

return preferred_term
$$ LANGUAGE plpythonu;

-- The preferred term is the most looked up value ( looked up with concept_id ), so lets optimize that lookup
DROP MATERIALIZED VIEW IF EXISTS concept_preferred_terms CASCADE;
CREATE MATERIALIZED VIEW concept_preferred_terms AS
SELECT
  DISTINCT(con.component_id) as concept_id,
  get_preferred_term(array_agg(row_to_json((des.component_id, des.module_id, des.type_id, des.effective_time, des.case_significance_id, des.term, des.language_code, des.active, ref.acceptability_id, ref.refset_id)::description))) AS preferred_term
FROM snomed_concept con
LEFT JOIN snomed_description des ON des.concept_id = con.component_id
LEFT JOIN snomed_language_reference_set ref ON ref.referenced_component_id = des.component_id
GROUP BY con.component_id;
CREATE INDEX concept_preferred_terms_concept_id ON concept_preferred_terms(concept_id);

-- This is shared by all of the functions that "expand" descriptions into the form that will be served
CREATE OR REPLACE FUNCTION process_description(description json) RETURNS text AS $$
import ujson as json

descr = json.loads(description)

def _get_preferred_name(concept_id):
    return plpy.execute("SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = %s" % concept_id)[0]["preferred_term"]

return json.dumps({
    "description_id": descr["component_id"],
    "type_id": descr["type_id"],
    "type_name": _get_preferred_name(descr["type_id"]),
    "module_id": descr["module_id"],
    "module_name": _get_preferred_name(descr["module_id"]),
    "case_significance_id": descr["case_significance_id"],
    "case_significance_name": _get_preferred_name(descr["case_significance_id"]),
    "term": descr["term"],
    "active": descr["active"]
})
$$ LANGUAGE plpythonu;

-- The next three functions populate the aggregates / lists for various kinds of descriptions ( including one combined one )
CREATE OR REPLACE FUNCTION get_descriptions(descs json[]) RETURNS text AS $$
import ujson as json
descriptions = [json.loads(descr) for descr in descs]
plan = plpy.prepare("SELECT process_description($1) AS description", ["json"])
return json.dumps([
    plpy.execute(plan, [json.dumps(description)])[0]["description"]
    for description in descriptions
])
$$ LANGUAGE plpythonu;

CREATE OR REPLACE FUNCTION get_preferred_terms(descs json[]) RETURNS text AS $$
import ujson as json
descriptions = [json.loads(descr) for descr in descs]
plan = plpy.prepare("SELECT process_description($1) AS description", ["json"])
return json.dumps([
    plpy.execute(plan, [json.dumps(description)])[0]["description"]
    for description in descriptions
    if description["acceptability_id"] == 900000000000548007
])
$$ LANGUAGE plpythonu;

CREATE OR REPLACE FUNCTION get_synonyms(descs json[]) RETURNS text AS $$
import ujson as json
descriptions = [json.loads(descr) for descr in descs]
plan = plpy.prepare("SELECT process_description($1) AS description", ["json"])
return json.dumps([
    plpy.execute(plan, [json.dumps(description)])[0]["description"]
    for description in descriptions
    if description["acceptability_id"] in [900000000000549004, None] and description["type_id"] == 900000000000013009
])
$$ LANGUAGE plpythonu;

-- The next two functions ( and the previously defined preferred_term one ) return a single text value
CREATE OR REPLACE FUNCTION get_fully_specified_name(descs json[]) RETURNS text AS $$
import ujson as json
descriptions = [json.loads(descr) for descr in descs]
for descr in descriptions:
    if descr["type_id"] == 900000000000003001:
        return descr["term"]

# We should have returned a fully specified name by now
raise Exception("No fully specified name found; this should not happen ( programming error )")
$$ LANGUAGE plpythonu;

CREATE OR REPLACE FUNCTION get_definition(descs json[]) RETURNS text AS $$
import ujson as json
descriptions = [json.loads(descr) for descr in descs]
for descr in descriptions:
    if descr["type_id"] == 900000000000550004:
        return descr["term"]

# It is possible for the definition to be blank
return ""
$$ LANGUAGE plpythonu;

CREATE OR REPLACE FUNCTION process_relationships(rels text) RETURNS text AS $$
import ujson as json

def _get_preferred_name(concept_id):
    return plpy.execute("SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = %s" % concept_id)[0]["preferred_term"]

def _process_relationship(rel):
    return {
        "relationship_id": rel["relationship_id"],
        "concept_id": rel["concept_id"],
        "concept_name": _get_preferred_name(rel["concept_id"])
    }

return json.dumps([_process_relationship(rel) for rel in json.loads(rels)])
$$ LANGUAGE plpythonu;

CREATE OR REPLACE FUNCTION is_navigation_concept(concept_id bigint) RETURNS boolean AS $$
import json

children = json.loads(plpy.execute("SELECT is_a_children FROM snomed_subsumption WHERE concept_id = 363743006")[0]["is_a_children"])
for child in children:
    if concept_id == json.loads(child)["concept_id"]:
        return True
return False
$$ LANGUAGE plpythonu;
-- This view here was originally a common table expression which was too slow ( explains the name? )
DROP MATERIALIZED VIEW IF EXISTS con_desc_cte;
CREATE MATERIALIZED VIEW con_desc_cte AS
SELECT
    DISTINCT(conc.component_id) AS concept_id,
    conc.effective_time, conc.active, conc.module_id, conc.definition_status_id,
    CASE WHEN conc.definition_status_id = 900000000000074008 THEN true ELSE false END AS is_primitive,
    is_navigation_concept(conc.component_id) AS is_navigation_concept,
    array_agg(row_to_json((des.component_id, des.module_id, des.type_id, des.effective_time, des.case_significance_id, des.term, des.language_code, des.active, ref.acceptability_id, ref.refset_id)::description)) AS descs
  FROM snomed_concept conc
  LEFT JOIN snomed_description des ON des.concept_id = conc.component_id
  LEFT JOIN snomed_language_reference_set ref ON ref.referenced_component_id = des.component_id
  GROUP BY conc.component_id, conc.effective_time, conc.active, conc.module_id, conc.definition_status_id, is_primitive, is_navigation_concept;
CREATE INDEX con_desc_cte_concept_id ON con_desc_cte(concept_id);
-- The final output view
DROP MATERIALIZED VIEW IF EXISTS concept_expanded_view CASCADE;
CREATE MATERIALIZED VIEW concept_expanded_view AS
SELECT
    -- Straight forward retrieval from the concept table
    con_desc.concept_id, con_desc.effective_time, con_desc.active, con_desc.module_id, con_desc.definition_status_id,
    CASE WHEN con_desc.definition_status_id = 900000000000074008 THEN true ELSE false END AS is_primitive,
    is_navigation_concept(con_desc.component_id) AS is_navigation_concept,
    -- The next three fields should contain plain text
    get_fully_specified_name(con_desc.descs) AS fully_specified_name,
    get_preferred_term(con_desc.descs)::text AS preferred_term,
    get_definition(con_desc.descs) AS definition,
    -- For the next three fields, use a format that is close to the final inlined format for descriptions
    get_descriptions(con_desc.descs) AS descriptions,
    get_preferred_terms(con_desc.descs) AS preferred_terms,
    get_synonyms(con_desc.descs) AS synonyms,
    -- Relationships - add preferred term of referenced concepts
    process_relationships(sub.is_a_parents) AS is_a_parents,
    process_relationships(sub.is_a_children) AS is_a_children,
    process_relationships(sub.is_a_direct_parents) AS is_a_direct_parents,
    process_relationships(sub.is_a_direct_children) AS is_a_direct_children,
    process_relationships(sub.part_of_parents) AS part_of_parents,
    process_relationships(sub.part_of_children) AS part_of_children,
    process_relationships(sub.part_of_direct_parents) AS part_of_direct_parents,
    process_relationships(sub.part_of_direct_children) AS part_of_direct_children,
    process_relationships(sub.other_parents) AS other_parents,
    process_relationships(sub.other_children) AS other_children,
    process_relationships(sub.other_direct_parents) AS other_direct_parents,
    process_relationships(sub.other_direct_children) AS other_direct_children
FROM con_desc_cte con_desc
LEFT JOIN snomed_subsumption sub ON sub.concept_id = con_desc.concept_id
GROUP BY
  con_desc.concept_id, con_desc.effective_time, con_desc.active, con_desc.module_id, con_desc.definition_status_id, is_primitive, is_navigation_concept,
  sub.is_a_parents, sub.is_a_children, sub.is_a_direct_parents, sub.is_a_direct_children,
  sub.part_of_parents, sub.part_of_children, sub.part_of_direct_parents, sub.part_of_direct_children,
  sub.other_parents, sub.other_children, sub.other_direct_parents, sub.other_direct_children,
  descriptions, preferred_terms, synonyms, fully_specified_name, preferred_term, definition

CREATE INDEX concept_expanded_view_concept_id ON concept_expanded_view(concept_id);
"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20140716_2059'),
    ]

    operations = [
        migrations.RunSQL(SQL),
    ]
