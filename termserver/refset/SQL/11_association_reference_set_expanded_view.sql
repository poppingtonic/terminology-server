CREATE MATERIALIZED VIEW association_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.target_component_id, get_concept_preferred_term(rf.target_component_id) AS target_component_name
  FROM snomed_association_reference_set rf;
