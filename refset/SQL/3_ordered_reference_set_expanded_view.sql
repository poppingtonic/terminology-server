CREATE MATERIALIZED VIEW ordered_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active, rf.order,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.linked_to_id, get_concept_preferred_term(rf.linked_to_id) AS linked_to_name
  FROM snomed_ordered_reference_set rf;
