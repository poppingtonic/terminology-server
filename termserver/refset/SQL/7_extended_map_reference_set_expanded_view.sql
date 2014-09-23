CREATE MATERIALIZED VIEW extended_map_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active,
    rf.module_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.module_id) AS module_name,
    rf.refset_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.refset_id) AS refset_name,
    rf.referenced_component_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.referenced_component_id) AS referenced_component_name,
    rf.correlation_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.correlation_id) AS correlation_name,
    rf.map_category_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rf.map_category_id) AS map_category_name,
    rf.map_group, rf.map_priority, rf.map_rule, rf.map_advice, rf.map_target
  FROM snomed_extended_map_reference_set rf;
