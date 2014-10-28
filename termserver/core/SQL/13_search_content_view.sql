CREATE MATERIALIZED VIEW search_content_view AS
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
  ARRAY(SELECT concept_id FROM unnest(conc.is_a_children)) AS is_a_children_ids
FROM concept_expanded_view conc;
