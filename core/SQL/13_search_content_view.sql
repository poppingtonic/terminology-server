CREATE VIEW search_content_view AS
SELECT
  conc.id,
  conc.concept_id,
  conc.active,
  conc.is_primitive,
  conc.module_id,
  conc.module_name,
  (conc.fully_specified_name).term AS fully_specified_name,
  (conc.preferred_term).term AS preferred_term,
  ARRAY(SELECT term FROM unnest(conc.descriptions)) AS descriptions,
  ARRAY(SELECT concept_id FROM unnest(conc.is_a_parents)) AS is_a_parent_ids,
  ARRAY(SELECT concept_id FROM unnest(conc.is_a_children)) AS is_a_children_ids,
  ARRAY(
      SELECT DISTINCT(refset_id) FROM snomed_simple_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_ordered_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_attribute_value_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_simple_map_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_complex_map_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_extended_map_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_query_specification_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_annotation_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_association_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_module_dependency_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_description_format_reference_set WHERE referenced_component_id = conc.concept_id INTERSECT
      SELECT DISTINCT(refset_id) FROM snomed_reference_set_descriptor_reference_set WHERE referenced_component_id = conc.concept_id
  ) AS refset_ids
FROM concept_expanded_view conc;

