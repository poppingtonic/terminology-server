CREATE MATERIALIZED VIEW reference_set_descriptor_reference_set_expanded_view AS
  SELECT
    rf.id, rf.row_id, rf.effective_time, rf.active, rf.attribute_order,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.attribute_description_id, get_concept_preferred_term(rf.attribute_description_id) AS attribute_description_name,
    rf.attribute_type_id, get_concept_preferred_term(rf.attribute_type_id) AS attribute_type_name
  FROM snomed_reference_set_descriptor_reference_set rf;
