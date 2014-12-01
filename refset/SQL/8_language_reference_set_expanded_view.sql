CREATE MATERIALIZED VIEW language_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id,
    (SELECT term FROM snomed_description WHERE component_id = rf.referenced_component_id LIMIT 1) AS referenced_component_name,
    rf.acceptability_id, get_concept_preferred_term(rf.acceptability_id) AS acceptability_name
  FROM snomed_language_reference_set rf;
