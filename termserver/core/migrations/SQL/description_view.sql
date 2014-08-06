CREATE MATERIALIZED VIEW description_expanded_view AS
  SELECT
    descr.id, descr.component_id, descr.effective_time, descr.active, descr.language_code, descr.term,
    descr.module_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = descr.module_id) AS module_name,
    descr.concept_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = descr.concept_id) AS concept_name,
    descr.type_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = descr.type_id) AS type_name,
    descr.case_significance_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = descr.case_significance_id) AS case_significance_name
  FROM snomed_description descr;
CREATE INDEX description_expanded_view_id ON description_expanded_view(id);
CREATE INDEX description_expanded_view_component_id ON description_expanded_view(component_id);
