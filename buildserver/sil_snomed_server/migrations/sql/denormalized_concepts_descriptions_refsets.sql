-- TODO: get definitions using materialized view

CREATE TYPE denormalized_description AS (
    component_id bigint,
    term text,
    acceptability_id bigint,
    refset_id bigint,
    type_id bigint
);

CREATE OR REPLACE FUNCTION get_preferred_term(descs denormalized_description[]) RETURNS text AS $$
SELECT  term from unnest(descs)
WHERE acceptability_id = 900000000000548007
AND refset_id IN (900000000000508004, 999001251000000103, 999000681000001101);
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION get_term_from_denormalized_description(ddesc denormalized_description) RETURNS text AS $$
SELECT (ddesc).term;
$$ LANGUAGE SQL;


CREATE TYPE expanded_concept AS (
    concept_id bigint,
    preferred_term text,
    fully_specified_name text
);

CREATE MATERIALIZED VIEW concept_preferred_terms AS
SELECT
  con.id as concept_id,
  get_preferred_term(array_agg((des.id, des.term, ref.acceptability_id, ref.refset_id, des.type_id)::denormalized_description)) AS preferred_term
FROM current_concept_snapshot con
JOIN current_description_snapshot des ON des.concept_id = con.id
JOIN current_language_reference_set_snapshot ref ON ref.referenced_component_id = des.id
GROUP BY con.id;

CREATE UNIQUE INDEX concept_preferred_terms_concept_id ON concept_preferred_terms (concept_id);

CREATE OR REPLACE FUNCTION extract_fully_specified_name(descs denormalized_description[])
RETURNS denormalized_description AS $$
    SELECT descr FROM unnest(descs) descr WHERE descr.type_id = 900000000000003001 LIMIT 1;
$$ LANGUAGE SQL;

CREATE MATERIALIZED VIEW concept_fully_specified_names AS
SELECT
  con.id as concept_id,
  extract_fully_specified_name(array_agg((des.id, des.term, ref.acceptability_id, ref.refset_id, des.type_id)::denormalized_description)) AS fully_specified_name
FROM current_concept_snapshot con
JOIN current_description_snapshot des ON des.concept_id = con.id
JOIN current_language_reference_set_snapshot ref ON ref.referenced_component_id = des.id
GROUP BY con.id;

CREATE UNIQUE INDEX concept_fully_specified_name_concept_id ON concept_fully_specified_names (concept_id);

CREATE OR REPLACE FUNCTION get_concept_preferred_term(bigint) returns text AS $$
    SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = $1;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION get_concept_fully_specified_name(bigint) returns text AS $$
    SELECT get_term_from_denormalized_description(fully_specified_name) FROM concept_fully_specified_names WHERE concept_id = $1;
$$ LANGUAGE SQL;


CREATE MATERIALIZED VIEW concept_subsumption AS
SELECT
    concept.id,
    ARRAY(SELECT
        destination_id
        FROM current_relationship_snapshot
        WHERE source_id = concept.id
        AND type_id = 116680003
        AND active=true) AS parents,
    ARRAY(SELECT
        supertype_id
        FROM single_snapshot_transitive_closure
        WHERE subtype_id = concept.id) AS ancestors,
    ARRAY(SELECT source_id
        FROM current_relationship_snapshot
        WHERE destination_id = concept.id
        AND type_id = 116680003
        AND active=true) AS children,
    ARRAY(SELECT subtype_id
        FROM single_snapshot_transitive_closure
        WHERE supertype_id = concept.id) AS descendants
FROM current_concept_snapshot concept;

create index denormalized_full_relationship_id on concept_subsumption (id);


-- This index here plays an outsized role in the creation of the language_reference_set_expanded_view
CREATE INDEX current_description_snapshot_id ON current_description_snapshot(id);
CREATE MATERIALIZED VIEW language_reference_set_expanded_view AS
  SELECT
    rf.id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id,
    (SELECT term FROM current_description_snapshot WHERE id = rf.referenced_component_id LIMIT 1) AS referenced_component_name,
    rf.acceptability_id, get_concept_preferred_term(rf.acceptability_id) AS acceptability_name
  FROM current_language_reference_set_snapshot rf;
CREATE UNIQUE INDEX language_reference_set_expanded_view_id ON language_reference_set_expanded_view(id);
CREATE INDEX language_reference_set_expanded_view_referenced_component_id ON language_reference_set_expanded_view(referenced_component_id);
CREATE INDEX language_reference_set_expanded_view_refset_id ON language_reference_set_expanded_view(refset_id);


CREATE INDEX ix_language_reference_set_expanded_view_referenced_component_id ON language_reference_set_expanded_view (referenced_component_id);


CREATE OR REPLACE FUNCTION expand_concept(id bigint)
RETURNS expanded_concept AS $$
  SELECT
  (id,
   get_concept_preferred_term(id),
   get_concept_fully_specified_name(id))::expanded_concept
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION extract_expanded_concepts_for_ancestors(concept_id bigint)
RETURNS expanded_concept[] AS $$
  DECLARE
    rel_ancestors bigint[];
    ancestor bigint;
    expanded_concepts expanded_concept[];
  BEGIN
    rel_ancestors := (SELECT ancestors
      FROM concept_subsumption
      WHERE id = concept_id);
    FOREACH ancestor IN ARRAY rel_ancestors LOOP
      expanded_concepts := expanded_concepts || expand_concept(ancestor);
    END LOOP;
    RETURN expanded_concepts;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION extract_expanded_concepts_for_descendants(concept_id bigint)
RETURNS expanded_concept[] AS $$
  DECLARE
    rel_descendants bigint[];
    descendant bigint;
    expanded_concepts expanded_concept[];
  BEGIN
    rel_descendants := (SELECT descendants
      FROM concept_subsumption
      WHERE id = concept_id);
    FOREACH descendant IN ARRAY rel_descendants LOOP
      expanded_concepts := expanded_concepts || expand_concept(descendant);
    END LOOP;
    RETURN expanded_concepts;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION extract_expanded_concepts_for_children(concept_id bigint)
RETURNS expanded_concept[] AS $$
  DECLARE
    rel_children bigint[];
    child bigint;
    expanded_concepts expanded_concept[];
  BEGIN
    rel_children := (SELECT children
      FROM concept_subsumption
      WHERE id = concept_id);
    FOREACH child IN ARRAY rel_children LOOP
      expanded_concepts := expanded_concepts || expand_concept(child);
    END LOOP;
    RETURN expanded_concepts;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION extract_expanded_concepts_for_parents(concept_id bigint)
RETURNS expanded_concept[] AS $$
  DECLARE
    rel_parents bigint[];
    parent bigint;
    expanded_concepts expanded_concept[];
  BEGIN
    rel_parents := (SELECT parents
      FROM concept_subsumption
      WHERE id = concept_id);
    FOREACH parent IN ARRAY rel_parents LOOP
      expanded_concepts := expanded_concepts || expand_concept(parent);
    END LOOP;
    RETURN expanded_concepts;
END;
$$ LANGUAGE plpgsql;


CREATE TYPE denormalized_reference_set_identifier AS (
       refset_id bigint,
       refset_type text
);


-- Denormalize all refsets into this matview, so that we can store them as the type defined above in the respective components
CREATE MATERIALIZED VIEW snomed_denormalized_refset_view_for_current_snapshot AS
SELECT
    ref.referenced_component_id, ref.refset_id, 'ASSOCIATION' refset_type
FROM
    current_association_reference_set_snapshot ref
WHERE ref.active = true
UNION
SELECT
    ref.referenced_component_id, ref.refset_id, 'ATTRIBUTE_VALUE' refset_type
FROM
    current_attribute_value_reference_set_snapshot ref
WHERE ref.active = true
UNION
SELECT
    ref.referenced_component_id, ref.refset_id, 'COMPLEX_MAP' refset_type
FROM
    current_complex_map_reference_set_snapshot ref
WHERE ref.active = true
UNION
SELECT
    ref.referenced_component_id, ref.refset_id, 'SIMPLE' refset_type
FROM
    current_simple_reference_set_snapshot ref
WHERE ref.active = true
UNION
SELECT
    ref.referenced_component_id, ref.refset_id, 'ORDERED' refset_type
FROM
    current_ordered_reference_set_snapshot ref
WHERE ref.active = true
UNION
SELECT
    ref.referenced_component_id, ref.refset_id, 'SIMPLE_MAP' refset_type
FROM
    current_simple_map_reference_set_snapshot ref
WHERE ref.active = true
UNION
SELECT
    ref.referenced_component_id, ref.refset_id, 'QUERY_SPECIFICATION' refset_type
FROM
    current_query_specification_reference_set_snapshot ref
WHERE ref.active = true
UNION
SELECT
    ref.referenced_component_id, ref.refset_id, 'MODULE_DEPENDENCY' refset_type
FROM
    current_module_dependency_reference_set_snapshot ref
WHERE ref.active = true
UNION
SELECT
    ref.referenced_component_id, ref.refset_id, 'REFERENCE_SET_DESCRIPTOR' refset_type
FROM
    current_reference_set_descriptor_reference_set_snapshot ref
WHERE ref.active = true
UNION
SELECT
    ref.referenced_component_id, ref.refset_id, 'EXTENDED_MAP' refset_type
FROM
    current_extended_map_reference_set_snapshot ref
WHERE ref.active = true
UNION
SELECT
    ref.referenced_component_id, ref.refset_id, 'ANNOTATION' refset_type
FROM
    current_annotation_reference_set_snapshot ref
WHERE ref.active = true
UNION
SELECT
    ref.referenced_component_id, ref.refset_id, 'DESCRIPTION_FORMAT' refset_type
FROM
    current_description_format_reference_set_snapshot ref
WHERE ref.active = true
UNION
SELECT
    ref.referenced_component_id, ref.refset_id, 'LANGUAGE' refset_type
FROM
    current_language_reference_set_snapshot ref
WHERE ref.active = true;

CREATE INDEX ix_snomed_denormalized_refset_view_referenced_component_id ON snomed_denormalized_refset_view_for_current_snapshot (referenced_component_id);


-- include refsets that the relationship is in, to support the search for qualifiers
CREATE MATERIALIZED VIEW snomed_denormalized_relationship_for_current_snapshot AS SELECT
    relationship.id,
    relationship.effective_time,
    relationship.active,
    relationship.module_id,
    get_concept_preferred_term(relationship.module_id) module_name,
    relationship.relationship_group,
    relationship.source_id,
    get_concept_preferred_term(relationship.source_id) source_name,
    relationship.destination_id,
    get_concept_preferred_term(relationship.destination_id) destination_name,
    relationship.type_id,
    get_concept_preferred_term(relationship.type_id) type_name,
    relationship.characteristic_type_id,
    get_concept_preferred_term(relationship.characteristic_type_id) characteristic_type_name,
    relationship.modifier_id,
    get_concept_preferred_term(relationship.modifier_id) modifier_name
FROM current_relationship_snapshot relationship;

CREATE TYPE denormalized_relationship_type AS (
       id bigint,
       effective_time date,
       active boolean,
       module_id bigint,
       module_name text,
       relationship_group integer,
       source_id bigint,
       source_name text,
       destination_id bigint,
       destination_name text,
       type_id bigint,
       type_name text,
       characteristic_type_id bigint,
       characteristic_type_name text,
       modifier_id bigint,
       modifier_name text
);


CREATE INDEX denormalized_relationship_source_id ON snomed_denormalized_relationship_for_current_snapshot (source_id);
CREATE INDEX snomed_denormalized_relationship_partial_index_type_id ON snomed_denormalized_relationship_for_current_snapshot (type_id) WHERE type_id = 116680003;
CREATE INDEX denormalized_relationship_destination_id ON snomed_denormalized_relationship_for_current_snapshot (destination_id);


CREATE MATERIALIZED VIEW denormalized_description_for_current_snapshot AS
SELECT
    description.id,
    description.effective_time,
    description.active,
    description.module_id,
    get_concept_preferred_term(description.module_id) module_name,
    description.language_code,
    description.type_id,
    get_concept_preferred_term(description.type_id) type_name,
    description.term,
    description.case_significance_id,
    get_concept_preferred_term(description.case_significance_id) case_significance_name,
    description.concept_id,
    array_to_json(ARRAY(SELECT (ref.refset_id, ref.refset_type)::denormalized_reference_set_identifier FROM snomed_denormalized_refset_view_for_current_snapshot ref WHERE referenced_component_id = description.id)) reference_set_memberships
FROM current_description_snapshot description;

CREATE INDEX denormalized_description_concept_id ON denormalized_description_for_current_snapshot (concept_id);
CREATE INDEX denormalized_description_id ON denormalized_description_for_current_snapshot (id);
CREATE INDEX denormalized_description_type_id ON denormalized_description_for_current_snapshot (type_id);
CREATE INDEX partial_denormalized_index_for_type_id_fsn ON denormalized_description_for_current_snapshot (type_id) WHERE type_id = 900000000000003001;


-- {"id":<sctid>, "typeId":<>, "typeName":<>, "term":<the actual description>, "caseSignificanceId":<sctid>, "caseSignificanceName":<preferred>}
CREATE TYPE denormalized_description_type AS (
       id bigint,
       type_id bigint,
       type_name text,
       term text,
       case_significance_id bigint,
       case_significance_name text
);

-- To serve the creation of an adjancency list data file,
-- prepend the children array with the concept id, then concatenate the resultant array's elements with a single space
CREATE OR REPLACE FUNCTION get_adjacency_list(id bigint, children bigint[]) RETURNS text AS $get_adjacency_list$
BEGIN
    return concat_ws(' ', VARIADIC array_prepend(id, children));
END;
$get_adjacency_list$
LANGUAGE plpgsql IMMUTABLE;

-- Converts all terms in the descriptions array of a concept to tsvectors
CREATE OR REPLACE FUNCTION get_tsvector_from_json(descriptions json) RETURNS tsvector AS $get_tsvector$
DECLARE
   terms text;
BEGIN
   terms := concat_ws('|', VARIADIC ARRAY(select distinct json_extract_path(json_array_elements(descriptions), 'term')::text));
   return to_tsvector('english', terms);
END;
$get_tsvector$
LANGUAGE plpgsql IMMUTABLE;
