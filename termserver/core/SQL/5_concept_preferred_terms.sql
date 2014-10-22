CREATE MATERIALIZED VIEW concept_preferred_terms AS
SELECT
  con.component_id as concept_id,
  get_preferred_term(array_agg((des.term, ref.acceptability_id, ref.refset_id)::shortened_description)) AS preferred_term
FROM snomed_concept con
LEFT JOIN snomed_description des ON des.concept_id = con.component_id
LEFT JOIN snomed_language_reference_set ref ON ref.referenced_component_id = des.component_id
GROUP BY con.component_id;


CREATE OR REPLACE FUNCTION get_concept_preferred_term(bigint) returns text AS $$
    SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = $1;
$$ LANGUAGE SQL;
