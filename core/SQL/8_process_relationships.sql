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
