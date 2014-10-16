CREATE MATERIALIZED VIEW relationship_expanded_view AS
  SELECT
    rel.id, rel.component_id, rel.effective_time, rel.active, rel.relationship_group,
    rel.module_id, get_concept_preferred_term(rel.module_id) AS module_name,
    rel.source_id, get_concept_preferred_term(rel.source_id) AS source_name,
    rel.destination_id, get_concept_preferred_term(rel.destination_id) AS destination_name,
    rel.type_id, get_concept_preferred_term(rel.type_id) AS type_name,
    rel.characteristic_type_id, get_concept_preferred_term(rel.characteristic_type_id) AS characteristic_type_name,
    rel.modifier_id, get_concept_preferred_term(rel.modifier_id) AS modifier_name
  FROM snomed_relationship rel;
