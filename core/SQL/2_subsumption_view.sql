CREATE MATERIALIZED VIEW snomed_subsumption AS
SELECT
  concept_id,
  is_a_direct_parents, is_a_parents, is_a_direct_children, is_a_children,
  part_of_direct_parents, part_of_parents, part_of_direct_children, part_of_children,
  other_direct_parents, other_parents, other_direct_children, other_children
FROM generate_subsumption_maps();
