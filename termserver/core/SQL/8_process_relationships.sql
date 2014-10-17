CREATE TYPE expanded_relationship AS (
    concept_id bigint,
    concept_name text
)

CREATE TYPE relationship_result AS (
    is_a_parents expanded_relationship[],
    is_a_children expanded_relationship[],
    is_a_direct_parents expanded_relationship[],
    is_a_direct_children expanded_relationship[],
    part_of_parents expanded_relationship[],
    part_of_children expanded_relationship[],
    part_of_direct_parents expanded_relationship[],
    part_of_direct_children expanded_relationship[],
    other_parents expanded_relationship[],
    other_children expanded_relationship[],
    other_direct_parents expanded_relationship[],
    other_direct_children expanded_relationship[]
);

CREATE OR REPLACE FUNCTION expand_relationships(rels bigint[])
RETURNS SETOF expanded_relationship AS $$
    SELECT rel_id, get_concept_preferred_term(rel_id)
    FROM unnest(rels)
    AS rel_id;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION process_relationships(sub snomed_subsumption)
RETURNS relationship_result AS $$
    SELECT
        expand_relationships(sub.is_a_parents),
        expand_relationships(sub.is_a_children),
        expand_relationships(sub.is_a_direct_parents),
        expand_relationships(sub.is_a_direct_children),
        expand_relationships(sub.part_of_parents),
        expand_relationships(sub.part_of_children),
        expand_relationships(sub.part_of_direct_parents),
        expand_relationships(sub.part_of_direct_children),
        expand_relationships(sub.other_parents),
        expand_relationships(sub.other_children),
        expand_relationships(sub.other_direct_parents),
        expand_relationships(sub.other_direct_children);
$$ LANGUAGE SQL;
