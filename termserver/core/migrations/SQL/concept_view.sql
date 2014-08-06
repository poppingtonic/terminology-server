-- We need this custom type so that we can aggregate all the information that relates to one description together
DROP TYPE IF EXISTS description CASCADE;
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
  con.component_id as concept_id,
  get_preferred_term(array_agg(row_to_json((des.component_id, des.module_id, des.type_id, des.effective_time, des.case_significance_id, des.term, des.language_code, des.active, ref.acceptability_id, ref.refset_id)::description))) AS preferred_term
FROM snomed_concept con
LEFT JOIN snomed_description des ON des.concept_id = con.component_id
LEFT JOIN snomed_language_reference_set ref ON ref.referenced_component_id = des.component_id
GROUP BY con.component_id;
CREATE INDEX concept_preferred_terms_concept_id_term ON concept_preferred_terms(concept_id, preferred_term);

DROP TYPE IF EXISTS description_result CASCADE;
CREATE TYPE description_result AS (
    descriptions text,
    preferred_terms text,
    synonyms text,
    fully_specified_name text,
    definition text,
    preferred_term text
);
CREATE OR REPLACE FUNCTION process_descriptions(descs json[]) RETURNS description_result AS $$
import ujson as json
descriptions = [json.loads(descr) for descr in descs]

def _get_preferred_name(concept_id):
    return plpy.execute("SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = %s" % concept_id)[0]["preferred_term"]

def _process_description(descr):
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

def _get_fully_specified_name():
    for descr in descriptions:
        if descr["type_id"] == 900000000000003001:
            return descr["term"]

    # We should have returned a fully specified name by now
    raise Exception("No fully specified name found; this should not happen ( programming error )")

def _get_definition():
    for descr in descriptions:
        if descr["type_id"] == 900000000000550004:
            return descr["term"]

    # It is possible for the definition to be blank
    return ""

def _get_preferred_term():
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

    # Finally, return it
    return preferred_term

return (
    json.dumps([
        _process_description(description)
        for description in descriptions
    ]),
    json.dumps([
        _process_description(description)
        for description in descriptions
        if description["acceptability_id"] == 900000000000548007
    ]),
    json.dumps([
        _process_description(description)
        for description in descriptions
        if description["acceptability_id"] in [900000000000549004, None] and description["type_id"] == 900000000000013009
    ]),
    _get_fully_specified_name(),
    _get_definition(),
    _get_preferred_term()
)
$$ LANGUAGE plpythonu;


CREATE OR REPLACE FUNCTION process_relationships(rels text) RETURNS text AS $$
import ujson as json

def _get_preferred_name(concept_id):
    return plpy.execute("SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = %s" % concept_id)[0]["preferred_term"]

def _process_relationship(relationship):
    rel = json.loads(relationship)
    return {
        "relationship_id": rel["relationship_id"],
        "concept_id": rel["concept_id"],
        "concept_name": _get_preferred_name(rel["concept_id"])
    }

return json.dumps([_process_relationship(rel) for rel in json.loads(rels)])
$$ LANGUAGE plpythonu;

-- This view here was originally a common table expression which was too slow ( explains the name? )
DROP MATERIALIZED VIEW IF EXISTS con_desc_cte;
CREATE MATERIALIZED VIEW con_desc_cte AS
SELECT
    conc.component_id AS concept_id,
    conc.effective_time, conc.active, conc.module_id, conc.definition_status_id,
    CASE WHEN conc.definition_status_id = 900000000000074008 THEN true ELSE false END AS is_primitive,
    array_agg(row_to_json((des.component_id, des.module_id, des.type_id, des.effective_time, des.case_significance_id, des.term, des.language_code, des.active, ref.acceptability_id, ref.refset_id)::description)) AS descs
  FROM snomed_concept conc
  LEFT JOIN snomed_description des ON des.concept_id = conc.component_id
  LEFT JOIN snomed_language_reference_set ref ON ref.referenced_component_id = des.component_id
  GROUP BY conc.component_id, conc.effective_time, conc.active, conc.module_id, conc.definition_status_id;
CREATE INDEX con_desc_cte_concept_id ON con_desc_cte(concept_id);

-- The final output view
DROP MATERIALIZED VIEW IF EXISTS concept_expanded_view CASCADE;
CREATE MATERIALIZED VIEW concept_expanded_view AS
SELECT
    -- Straight forward retrieval from the pre-processed view
    con_desc.concept_id, con_desc.effective_time, con_desc.active, con_desc.is_primitive,
    -- Look up the names of these attributes
    con_desc.module_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = con_desc.module_id) AS module_name,
    con_desc.definition_status_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = con_desc.definition_status_id) AS defintion_status_name,
    -- Get the descriptions from the stored procedure
    processed_descriptions.descriptions, processed_descriptions.preferred_terms, processed_descriptions.synonyms,
    processed_descriptions.fully_specified_name, processed_descriptions.definition, processed_descriptions.preferred_term,
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
LEFT JOIN LATERAL process_descriptions(con_desc.descs) processed_descriptions ON true
LEFT JOIN snomed_subsumption sub ON sub.concept_id = con_desc.concept_id;
CREATE INDEX concept_expanded_view_concept_id ON concept_expanded_view(concept_id);

