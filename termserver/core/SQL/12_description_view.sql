CREATE MATERIALIZED VIEW description_expanded_view AS
  SELECT
    descr.id, descr.component_id, descr.effective_time, descr.active, descr.language_code, descr.term,
    descr.module_id, get_concept_preferred_term(descr.module_id) AS module_name,
    descr.concept_id, get_concept_preferred_term(descr.concept_id) AS concept_name,
    descr.type_id, get_concept_preferred_term(descr.type_id) AS type_name,
    descr.case_significance_id, get_concept_preferred_term(descr.case_significance_id) AS case_significance_name
  FROM snomed_description descr;
