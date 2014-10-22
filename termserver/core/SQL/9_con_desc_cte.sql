-- This view here was originally a common table expression which was too slow ( explains the name? )
CREATE MATERIALIZED VIEW con_desc_cte AS
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
  WHERE conc.active = True
  GROUP BY conc.id, conc.component_id, conc.effective_time, conc.active, conc.module_id, conc.definition_status_id;
