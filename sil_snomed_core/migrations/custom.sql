-- SNAPSHOT VIEWS
-- This server loads full releases, but most work is done with the current snapshot
-- There are no extra indexes on the source tables, because these queries work best with sequential scans

CREATE VIEW snomed_concept AS
SELECT DISTINCT ON(comp.component_id)
   comp.*
FROM snomed_concept_full comp
ORDER BY comp.component_id, comp.effective_time DESC;

CREATE VIEW snomed_description AS
SELECT DISTINCT ON(comp.component_id)
   comp.*
FROM snomed_description_full comp
ORDER BY comp.component_id, comp.effective_time DESC;;

CREATE VIEW snomed_relationship AS
SELECT DISTINCT ON(comp.component_id)
   comp.*
FROM snomed_relationship_full comp
ORDER BY comp.component_id, comp.effective_time DESC;

CREATE VIEW snomed_annotation_reference_set AS
SELECT DISTINCT ON(refset.row_id)
   refset.*
FROM snomed_annotation_reference_set_full refset
ORDER BY refset.row_id, refset.effective_time DESC;

CREATE VIEW snomed_association_reference_set AS
SELECT DISTINCT ON(refset.row_id)
   refset.*
FROM snomed_association_reference_set_full refset
ORDER BY refset.row_id, refset.effective_time DESC;

CREATE VIEW snomed_attribute_value_reference_set AS
SELECT DISTINCT ON(refset.row_id)
   refset.*
FROM snomed_attribute_value_reference_set_full refset
ORDER BY refset.row_id, refset.effective_time DESC;

CREATE VIEW snomed_complex_map_reference_set AS
SELECT DISTINCT ON(refset.row_id)
   refset.*
FROM snomed_complex_map_reference_set_full refset
ORDER BY refset.row_id, refset.effective_time DESC;

CREATE VIEW snomed_description_format_reference_set AS
SELECT DISTINCT ON(refset.row_id)
   refset.*
FROM snomed_description_format_reference_set_full refset
ORDER BY refset.row_id, refset.effective_time DESC;;

CREATE VIEW snomed_extended_map_reference_set AS
SELECT DISTINCT ON(refset.row_id)
   refset.*
FROM snomed_extended_map_reference_set_full refset
ORDER BY refset.row_id, refset.effective_time DESC;

CREATE VIEW snomed_language_reference_set AS
SELECT DISTINCT ON(refset.row_id)
   refset.*
FROM snomed_language_reference_set_full refset
ORDER BY refset.row_id, refset.effective_time DESC;

CREATE VIEW snomed_module_dependency_reference_set AS
SELECT DISTINCT ON(refset.row_id)
   refset.*
FROM snomed_module_dependency_reference_set_full refset
ORDER BY refset.row_id, refset.effective_time DESC;;

CREATE VIEW snomed_ordered_reference_set AS
SELECT DISTINCT ON(refset.row_id)
   refset.*
FROM snomed_ordered_reference_set_full refset
ORDER BY refset.row_id, refset.effective_time DESC;;

CREATE VIEW snomed_query_specification_reference_set AS
SELECT DISTINCT ON(refset.row_id)
   refset.*
FROM snomed_query_specification_reference_set_full refset
ORDER BY refset.row_id, refset.effective_time DESC;;

CREATE VIEW snomed_reference_set_descriptor_reference_set AS
SELECT DISTINCT ON(refset.row_id)
   refset.*
FROM snomed_reference_set_descriptor_reference_set_full refset
ORDER BY refset.row_id, refset.effective_time DESC;;

CREATE VIEW snomed_simple_map_reference_set AS
SELECT DISTINCT ON(refset.row_id)
   refset.*
FROM snomed_simple_map_reference_set_full refset
ORDER BY refset.row_id, refset.effective_time DESC;

CREATE VIEW snomed_simple_reference_set AS
SELECT DISTINCT ON(refset.row_id)
   refset.*
FROM snomed_simple_reference_set_full refset
ORDER BY refset.row_id, refset.effective_time DESC;

-- SUBSUMPTION ( TRANSITIVE CLOSURE ) GRAPH
-- SNOMED's |IS A| implements a directed acyclic graph, with a single root concept ( "node" )
-- We use PL/Python ( and networkx ) to precompute an easy-to-query form of that graph
-- Please note that this graph is computed only for "active" relationships ( "edges" )

CREATE EXTENSION IF NOT EXISTS plpythonu;
CREATE OR REPLACE FUNCTION generate_subsumption_maps() RETURNS
TABLE(
    concept_id bigint,
    is_a_direct_parents bigint[], is_a_parents bigint[],
    is_a_direct_children bigint[], is_a_children bigint[],
    part_of_direct_parents bigint[], part_of_parents bigint[],
    part_of_direct_children bigint[], part_of_children bigint[],
    other_direct_parents bigint[], other_parents bigint[],
    other_direct_children bigint[], other_children bigint[]
) AS $$
import networkx as nx


def _get_transitive_closure_map():
    """Load SNOMED relationships into a networkx directed multi graph"""
    g = nx.MultiDiGraph()
    relationships = plpy.execute(
        "SELECT destination_id, source_id, type_id "
        "FROM snomed_relationship WHERE active = True"
    )
    for rel in relationships:
        g.add_edge(
            rel["destination_id"], rel["source_id"],
            type_id=rel["type_id"]
        )
    return g

# The primary graph, and sub-graphs for various types
G = _get_transitive_closure_map()
IS_A = nx.DiGraph(
    (source, target, attr) for source, target, attr in G.edges_iter(data=True)
    if attr['type_id'] == 116680003
)
PART_OF = nx.DiGraph(
    (source, target, attr) for source, target, attr in G.edges_iter(data=True)
    if attr['type_id'] == 123005000
)
OTHER = nx.DiGraph(
    (source, target, attr) for source, target, attr in G.edges_iter(data=True)
    if attr['type_id'] not in [116680003, 123005000]
)

# Release memory from the main graph; we have a hard 4GB limit on CircleCI
del G
import gc
gc.collect()  # Yeah, this is not Pythonic

def get_relationships(concept_id):
    """Extract a single concept's relationships"""
    return (
        concept_id,
        IS_A.predecessors(concept_id),
        list(nx.dag.ancestors(IS_A, concept_id)),
        IS_A.successors(concept_id),
        list(nx.dag.descendants(IS_A, concept_id)),
        PART_OF.predecessors(concept_id) if concept_id in PART_OF else [],
        list(nx.dag.ancestors(PART_OF, concept_id)) if concept_id in PART_OF else [],
        PART_OF.successors(concept_id) if concept_id in PART_OF else [],
        list(nx.dag.descendants(PART_OF, concept_id)) if concept_id in PART_OF else [],
        OTHER.predecessors(concept_id) if concept_id in OTHER else [],
        list(nx.dag.ancestors(OTHER, concept_id)) if concept_id in OTHER else [],
        OTHER.successors(concept_id) if concept_id in OTHER else [],
        list(nx.dag.descendants(OTHER, concept_id)) if concept_id in OTHER else [],
    )

concepts = plpy.execute(
    "SELECT DISTINCT component_id FROM snomed_concept WHERE active = True")
return (get_relationships(concept["component_id"]) for concept in concepts)
$$ LANGUAGE plpythonu;

-- Compute the subsumption view
CREATE MATERIALIZED VIEW snomed_subsumption AS
SELECT
  concept_id,
  is_a_direct_parents, is_a_parents, is_a_direct_children, is_a_children,
  part_of_direct_parents, part_of_parents, part_of_direct_children, part_of_children,
  other_direct_parents, other_parents, other_direct_children, other_children
FROM generate_subsumption_maps();
CREATE INDEX snomed_subsumption_concept_id ON snomed_subsumption(concept_id);


-- Custom types for descriptions
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
CREATE TYPE shortened_description AS (
    term text,
    acceptability_id bigint,
    refset_id bigint
);

CREATE OR REPLACE FUNCTION get_preferred_term(descs shortened_description[]) RETURNS text AS $$
    -- GB English is 900000000000508004
    -- UK English reference set is 999001251000000103
    -- UK Extension drug lang refset is 999000681000001101
    SELECT term FROM unnest(descs)
    WHERE acceptability_id = 900000000000548007
    AND refset_id IN (900000000000508004, 999001251000000103, 999000681000001101);
$$ LANGUAGE SQL;


-- The concept_preferred_terms view is one of the most heavily used views 
-- A lot of the views that come after this need to look up preferred terms
CREATE MATERIALIZED VIEW concept_preferred_terms AS
SELECT
  con.component_id as concept_id,
  get_preferred_term(array_agg((des.term, ref.acceptability_id, ref.refset_id)::shortened_description)) AS preferred_term
FROM snomed_concept con
JOIN snomed_description des ON des.concept_id = con.component_id
JOIN snomed_language_reference_set ref ON ref.referenced_component_id = des.component_id
GROUP BY con.component_id;
CREATE INDEX concept_preferred_terms_concept_id ON concept_preferred_terms(concept_id);


CREATE OR REPLACE FUNCTION get_concept_preferred_term(bigint) returns text AS $$
    SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = $1;
$$ LANGUAGE SQL;
CREATE TYPE denormalized_description AS (
    component_id bigint,
    module_id bigint,
    module_name text,
    type_id bigint,
    type_name text,
    effective_time date,
    case_significance_id bigint,
    case_significance_name text,
    term text,
    language_code character varying(2),
    active boolean,
    acceptability_id bigint,
    acceptability_name text,
    refset_id bigint,
    refset_name text
);
CREATE OR REPLACE FUNCTION extract_fully_specified_name(descs denormalized_description[])
RETURNS denormalized_description AS $$
    SELECT descr FROM unnest(descs) descr WHERE descr.type_id = 900000000000003001 LIMIT 1;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION extract_definition(descs denormalized_description[])
RETURNS denormalized_description AS $$
    SELECT descr FROM unnest(descs) descr WHERE descr.type_id = 900000000000550004 LIMIT 1;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION extract_preferred_term(descs denormalized_description[])
RETURNS denormalized_description AS $$
    SELECT descr FROM unnest(descs) descr WHERE descr.type_id = 900000000000013009
    AND descr.refset_id IN (900000000000508004, 999001251000000103, 999000681000001101)
    LIMIT 1;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION extract_preferred_terms(descs denormalized_description[])
RETURNS denormalized_description[] AS $$
    SELECT array_agg(descr) FROM unnest(descs) descr WHERE descr.type_id = 900000000000013009
    AND descr.acceptability_id = 900000000000548007;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION extract_synonyms(descs denormalized_description[])
RETURNS denormalized_description[] AS $$
    SELECT array_agg(descr) FROM unnest(descs) descr WHERE descr.type_id = 900000000000013009
    AND descr.acceptability_id != 900000000000548007;
$$ LANGUAGE SQL;
CREATE TYPE expanded_relationship AS (
    concept_id bigint,
    concept_name text
);

CREATE OR REPLACE FUNCTION expand_relationships(rels bigint[])
RETURNS expanded_relationship[] AS $$
    SELECT array_agg(
        (rel_id, get_concept_preferred_term(rel_id))::expanded_relationship
    )
    FROM unnest(rels)
    AS rel_id;
$$ LANGUAGE SQL;

-- The final output view for concepts
-- This is arguably the single most important view
CREATE MATERIALIZED VIEW concept_expanded_view AS
WITH con_desc_cte AS (
SELECT
    conc.id as id, conc.component_id AS concept_id,
    conc.effective_time, conc.active, conc.module_id, conc.definition_status_id,
    CASE WHEN conc.definition_status_id = 900000000000074008 THEN true ELSE false END AS is_primitive,
    array_agg(
        (
            des.component_id,
            des.module_id,
            get_concept_preferred_term(des.module_id),
            des.type_id,
            get_concept_preferred_term(des.type_id),
            des.effective_time,
            des.case_significance_id,
            get_concept_preferred_term(des.case_significance_id),
            des.term,
            des.language_code,
            des.active,
            ref.acceptability_id,
            get_concept_preferred_term(ref.acceptability_id),
            ref.refset_id,
            get_concept_preferred_term(ref.refset_id)
        )::denormalized_description
    ) AS descs
  FROM snomed_concept conc
  JOIN snomed_description des ON des.concept_id = conc.component_id
  JOIN snomed_language_reference_set ref ON ref.referenced_component_id = des.component_id
  GROUP BY
    conc.id, conc.component_id, conc.effective_time, conc.active,
    conc.module_id, conc.definition_status_id
)
SELECT
    -- Straight forward retrieval from the pre-processed view
    con_desc.id, con_desc.concept_id, con_desc.effective_time, con_desc.active, con_desc.is_primitive,
    -- Look up the names of these attributes
    con_desc.module_id, get_concept_preferred_term(con_desc.module_id) AS module_name,
    con_desc.definition_status_id, get_concept_preferred_term(con_desc.definition_status_id) AS definition_status_name,
    -- Get the descriptions from the stored procedure
    con_desc.descs as descriptions,
    extract_preferred_terms(con_desc.descs) as preferred_terms,
    extract_synonyms(con_desc.descs) as synonyms,
    extract_fully_specified_name(con_desc.descs) as fully_specified_name,
    extract_definition(con_desc.descs) as definition,
    extract_preferred_term(con_desc.descs) as preferred_term,
    -- Relationships - use stored procedure to fill out
    expand_relationships(sub.is_a_parents) as is_a_parents,
    expand_relationships(sub.is_a_children) as is_a_children,
    expand_relationships(sub.is_a_direct_parents) as is_a_direct_parents,
    expand_relationships(sub.is_a_direct_children) as is_a_direct_children,
    expand_relationships(sub.part_of_parents) as part_of_parents,
    expand_relationships(sub.part_of_children) as part_of_children,
    expand_relationships(sub.part_of_direct_parents) as part_of_direct_parents,
    expand_relationships(sub.part_of_direct_children) as part_of_direct_children,
    expand_relationships(sub.other_parents) as other_parents,
    expand_relationships(sub.other_children) as other_children,
    expand_relationships(sub.other_direct_parents) as other_direct_parents,
    expand_relationships(sub.other_direct_children) as other_direct_children
FROM con_desc_cte con_desc
JOIN snomed_subsumption sub ON sub.concept_id = con_desc.concept_id;
CREATE UNIQUE INDEX concept_expanded_view_concept_id ON concept_expanded_view(concept_id);
CREATE UNIQUE INDEX concept_expanded_view_id ON concept_expanded_view(id);

CREATE MATERIALIZED VIEW relationship_expanded_view AS
  SELECT
    rel.id, rel.component_id, rel.effective_time, rel.active, rel.relationship_group,
    rel.module_id, get_concept_preferred_term(rel.module_id) AS module_name,
    rel.source_id, get_concept_preferred_term(rel.source_id) AS source_name,
    rel.destination_id, get_concept_preferred_term(rel.destination_id) AS destination_name,
    rel.type_id, get_concept_preferred_term(rel.type_id) AS type_name,
    rel.characteristic_type_id, get_concept_preferred_term(rel.characteristic_type_id) AS characteristic_type_name,
    rel.modifier_id, get_concept_preferred_term(rel.modifier_id) AS modifier_name
  FROM snomed_relationship rel;
CREATE UNIQUE INDEX relationship_expanded_view_component_id ON relationship_expanded_view(component_id);
CREATE UNIQUE INDEX relationship_expanded_view_id ON relationship_expanded_view(id);


CREATE MATERIALIZED VIEW description_expanded_view AS
  SELECT
    descr.id, descr.component_id, descr.effective_time, descr.active, descr.language_code, descr.term,
    descr.module_id, get_concept_preferred_term(descr.module_id) AS module_name,
    descr.concept_id, get_concept_preferred_term(descr.concept_id) AS concept_name,
    descr.type_id, get_concept_preferred_term(descr.type_id) AS type_name,
    descr.case_significance_id, get_concept_preferred_term(descr.case_significance_id) AS case_significance_name
  FROM snomed_description descr;
CREATE UNIQUE INDEX description_expanded_view_component_id ON description_expanded_view(component_id);
CREATE UNIQUE INDEX description_expanded_view_id ON description_expanded_view(id);


-- The search content view has no indexes because it is usually queried in bulk ( all of it retrieved at once )
-- Also: it is infrequently accessed
CREATE VIEW search_content_view AS
SELECT
  conc.id,
  conc.concept_id,
  conc.active,
  conc.is_primitive,
  conc.module_id,
  conc.module_name,
  (conc.fully_specified_name).term AS fully_specified_name,
  (conc.preferred_term).term AS preferred_term,
  ARRAY(SELECT term FROM unnest(conc.descriptions)) AS descriptions,
  ARRAY(SELECT concept_id FROM unnest(conc.is_a_parents)) AS is_a_parent_ids,
  ARRAY(SELECT concept_id FROM unnest(conc.is_a_children)) AS is_a_children_ids,
  ARRAY(
      SELECT DISTINCT(refset_id) FROM snomed_simple_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_ordered_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_attribute_value_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_simple_map_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_complex_map_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_extended_map_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_query_specification_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_annotation_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_association_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_module_dependency_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_description_format_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_reference_set_descriptor_reference_set WHERE referenced_component_id = conc.concept_id
  ) AS refset_ids
FROM concept_expanded_view conc;


CREATE MATERIALIZED VIEW reference_set_descriptor_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active, rf.attribute_order,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.attribute_description_id, get_concept_preferred_term(rf.attribute_description_id) AS attribute_description_name,
    rf.attribute_type_id, get_concept_preferred_term(rf.attribute_type_id) AS attribute_type_name
  FROM snomed_reference_set_descriptor_reference_set rf;
CREATE UNIQUE INDEX reference_set_descriptor_reference_set_expanded_view_id ON reference_set_descriptor_reference_set_expanded_view(id);
CREATE UNIQUE INDEX reference_set_descriptor_reference_set_expanded_view_row_id ON reference_set_descriptor_reference_set_expanded_view(row_id);


CREATE MATERIALIZED VIEW simple_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name
  FROM snomed_simple_reference_set rf;
CREATE UNIQUE INDEX simple_reference_set_expanded_view_id ON simple_reference_set_expanded_view(id);
CREATE UNIQUE INDEX simple_reference_set_expanded_view_row_id ON simple_reference_set_expanded_view(row_id);


CREATE MATERIALIZED VIEW ordered_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active, rf.order,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.linked_to_id, get_concept_preferred_term(rf.linked_to_id) AS linked_to_name
  FROM snomed_ordered_reference_set rf;
CREATE UNIQUE INDEX ordered_reference_set_expanded_view_id ON ordered_reference_set_expanded_view(id);
CREATE UNIQUE INDEX ordered_reference_set_expanded_view_row_id ON ordered_reference_set_expanded_view(row_id);


CREATE MATERIALIZED VIEW attribute_value_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.value_id, get_concept_preferred_term(rf.value_id) AS value_name
  FROM snomed_attribute_value_reference_set rf;
CREATE UNIQUE INDEX attribute_value_reference_set_expanded_view_id ON attribute_value_reference_set_expanded_view(id);
CREATE UNIQUE INDEX attribute_value_reference_set_expanded_view_row_id ON attribute_value_reference_set_expanded_view(row_id);


CREATE MATERIALIZED VIEW simple_map_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.map_target
  FROM snomed_simple_map_reference_set rf;
CREATE UNIQUE INDEX simple_map_reference_set_expanded_view_id ON simple_map_reference_set_expanded_view(id);
CREATE UNIQUE INDEX simple_map_reference_set_expanded_view_row_id ON simple_map_reference_set_expanded_view(row_id);


CREATE MATERIALIZED VIEW complex_map_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.correlation_id, get_concept_preferred_term(rf.correlation_id) AS correlation_name,
    rf.map_group, rf.map_priority, rf.map_rule, rf.map_advice, rf.map_target, rf.map_block
  FROM snomed_complex_map_reference_set rf;
CREATE UNIQUE INDEX complex_map_reference_set_expanded_view_id ON complex_map_reference_set_expanded_view(id);
CREATE UNIQUE INDEX complex_map_reference_set_expanded_view_row_id ON complex_map_reference_set_expanded_view(row_id);


CREATE MATERIALIZED VIEW extended_map_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.correlation_id, get_concept_preferred_term(rf.correlation_id) AS correlation_name,
    rf.map_category_id, get_concept_preferred_term(rf.map_category_id) AS map_category_name,
    rf.map_group, rf.map_priority, rf.map_rule, rf.map_advice, rf.map_target
  FROM snomed_extended_map_reference_set rf;
CREATE UNIQUE INDEX extended_map_reference_set_expanded_view_id ON extended_map_reference_set_expanded_view(id);
CREATE UNIQUE INDEX extended_map_reference_set_expanded_view_row_id ON extended_map_reference_set_expanded_view(row_id);


CREATE MATERIALIZED VIEW language_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id,
    (SELECT term FROM snomed_description WHERE component_id = rf.referenced_component_id LIMIT 1) AS referenced_component_name,
    rf.acceptability_id, get_concept_preferred_term(rf.acceptability_id) AS acceptability_name
  FROM snomed_language_reference_set rf;
CREATE UNIQUE INDEX language_reference_set_expanded_view_id ON language_reference_set_expanded_view(id);
CREATE UNIQUE INDEX language_reference_set_expanded_view_row_id ON language_reference_set_expanded_view(row_id);


CREATE MATERIALIZED VIEW query_specification_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.query
  FROM snomed_query_specification_reference_set rf;
CREATE UNIQUE INDEX query_specification_reference_set_expanded_view_id ON query_specification_reference_set_expanded_view(id);
CREATE UNIQUE INDEX query_specification_reference_set_expanded_view_row_id ON query_specification_reference_set_expanded_view(row_id);


CREATE MATERIALIZED VIEW annotation_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.annotation
  FROM snomed_annotation_reference_set rf;
CREATE UNIQUE INDEX annotation_reference_set_expanded_view_id ON annotation_reference_set_expanded_view(id);
CREATE UNIQUE INDEX annotation_reference_set_expanded_view_row_id ON annotation_reference_set_expanded_view(row_id);


CREATE MATERIALIZED VIEW association_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.target_component_id, get_concept_preferred_term(rf.target_component_id) AS target_component_name
  FROM snomed_association_reference_set rf;
CREATE UNIQUE INDEX association_reference_set_expanded_view_id ON association_reference_set_expanded_view(id);
CREATE UNIQUE INDEX association_reference_set_expanded_view_row_id ON association_reference_set_expanded_view(row_id);


CREATE MATERIALIZED VIEW module_dependency_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.source_effective_time, rf.target_effective_time
  FROM snomed_module_dependency_reference_set rf;
CREATE UNIQUE INDEX module_dependency_reference_set_expanded_view_id ON module_dependency_reference_set_expanded_view(id);
CREATE UNIQUE INDEX module_dependency_reference_set_expanded_view_row_id ON module_dependency_reference_set_expanded_view(row_id);


CREATE MATERIALIZED VIEW description_format_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.description_format_id, get_concept_preferred_term(rf.description_format_id) AS description_format_name,
    rf.description_length
  FROM snomed_description_format_reference_set rf;
CREATE UNIQUE INDEX description_format_reference_set_expanded_view_id ON description_format_reference_set_expanded_view(id);
CREATE UNIQUE INDEX description_format_reference_set_expanded_view_row_id ON description_format_reference_set_expanded_view(row_id);

-- A utility to make the refreshing of materialized views a one line affair
-- Source: https://github.com/sorokine/RefreshAllMaterializedViews/blob/master/RefreshAllMaterializedViews.sql
CREATE OR REPLACE FUNCTION RefreshAllMaterializedViews(schema_arg TEXT DEFAULT 'public')
RETURNS INT AS $$
    DECLARE
        r RECORD;
    BEGIN
        RAISE NOTICE 'Refreshing materialized view in schema %', schema_arg;
        FOR r IN SELECT matviewname FROM pg_matviews WHERE schemaname = schema_arg 
        LOOP
            RAISE NOTICE 'Refreshing %.%', schema_arg, r.matviewname;
            EXECUTE 'REFRESH MATERIALIZED VIEW ' || schema_arg || '.' || r.matviewname; 
        END LOOP;
        
        RETURN 1;
    END 
$$ LANGUAGE plpgsql;
