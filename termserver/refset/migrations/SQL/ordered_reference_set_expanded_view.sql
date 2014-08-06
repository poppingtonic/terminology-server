CREATE MATERIALIZED VIEW ordered_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active, rf.order,
    rf.module_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.module_id) AS module_name,
    rf.refset_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.refset_id) AS refset_name,
    rf.referenced_component_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.referenced_component_id) AS referenced_component_name,
    rf.linked_to_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.linked_to_id) AS linked_to_name
  FROM snomed_ordered_reference_set rf;
