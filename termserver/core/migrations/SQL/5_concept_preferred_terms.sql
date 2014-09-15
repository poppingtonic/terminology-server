CREATE MATERIALIZED VIEW concept_preferred_terms AS
SELECT
  con.component_id as concept_id,
  get_preferred_term(
    array_agg(
        row_to_json(
            (des.component_id, des.module_id, des.type_id, des.effective_time,
             des.case_significance_id, des.term, des.language_code, des.active,
             ref.acceptability_id, ref.refset_id)::description
        )
    )
) AS preferred_term
FROM snomed_concept con
LEFT JOIN snomed_description des ON des.concept_id = con.component_id
LEFT JOIN snomed_language_reference_set ref ON ref.referenced_component_id = des.component_id
GROUP BY con.component_id;
