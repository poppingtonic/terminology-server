COPY (SELECT
    get_adjacency_list(id, children) AS adjacency_list FROM concept_subsumption) TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/transitive_closure_adjacency_list.adjlist.gz';

COPY (
  SELECT
    * FROM language_reference_set_expanded_view) TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/language_reference_set_expanded_view.tsv.gz';

-- we copy these reference sets directly to tsv files, since they are only used in the termserver, not during the build step
COPY (
  SELECT
    rf.id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.attribute_description_id, get_concept_preferred_term(rf.attribute_description_id) AS attribute_description_name,
    rf.attribute_type_id, get_concept_preferred_term(rf.attribute_type_id) AS attribute_type_name,
    rf.attribute_order
  FROM current_reference_set_descriptor_reference_set_snapshot rf) TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/reference_set_descriptor_reference_set_expanded_view.tsv.gz';


COPY (
  SELECT
    rf.id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name
  FROM current_simple_reference_set_snapshot rf) TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/simple_reference_set_expanded_view.tsv.gz';


COPY (
  SELECT
    rf.id, rf.effective_time, rf.active, rf.order,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.linked_to_id, get_concept_preferred_term(rf.linked_to_id) AS linked_to_name
  FROM current_ordered_reference_set_snapshot rf) TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/ordered_reference_set_expanded_view.tsv.gz';


COPY (
  SELECT
    rf.id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.value_id, get_concept_preferred_term(rf.value_id) AS value_name
  FROM current_attribute_value_reference_set_snapshot rf) TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/attribute_value_reference_set_expanded_view.tsv.gz';


COPY (
  SELECT
    rf.id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.map_target
  FROM current_simple_map_reference_set_snapshot rf) TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/simple_map_reference_set_expanded_view.tsv.gz';


COPY (
  SELECT
    rf.id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.correlation_id, get_concept_preferred_term(rf.correlation_id) AS correlation_name,
    rf.map_group, rf.map_priority, rf.map_rule, rf.map_advice, rf.map_target, rf.map_block
  FROM current_complex_map_reference_set_snapshot rf) TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/complex_map_reference_set_expanded_view.tsv.gz';


COPY (
  SELECT
    rf.id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.correlation_id, get_concept_preferred_term(rf.correlation_id) AS correlation_name,
    rf.map_category_id, get_concept_preferred_term(rf.map_category_id) AS map_category_name,
    rf.map_group, rf.map_priority, rf.map_rule, rf.map_advice, rf.map_target
  FROM current_extended_map_reference_set_snapshot rf) TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/extended_map_reference_set_expanded_view.tsv.gz';


COPY (
  SELECT
    rf.id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.query
  FROM current_query_specification_reference_set_snapshot rf) TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/query_specification_reference_set_expanded_view.tsv.gz';


COPY (
  SELECT
    rf.id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.annotation
  FROM current_annotation_reference_set_snapshot rf) TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/annotation_reference_set_expanded_view.tsv.gz';


COPY (
  SELECT
    rf.id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.target_component_id, get_concept_preferred_term(rf.target_component_id) AS target_component_name
  FROM current_association_reference_set_snapshot rf) TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/association_reference_set_expanded_view.tsv.gz';


COPY (
  SELECT
    rf.id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.source_effective_time, rf.target_effective_time
  FROM current_module_dependency_reference_set_snapshot rf) TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/module_dependency_reference_set_expanded_view.tsv.gz';


COPY (
  SELECT
    rf.id, rf.effective_time, rf.active,
    rf.module_id, get_concept_preferred_term(rf.module_id) AS module_name,
    rf.refset_id, get_concept_preferred_term(rf.refset_id) AS refset_name,
    rf.referenced_component_id, get_concept_preferred_term(rf.referenced_component_id) AS referenced_component_name,
    rf.description_format_id, get_concept_preferred_term(rf.description_format_id) AS description_format_name,
    rf.description_length
  FROM current_description_format_reference_set_snapshot rf) TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/description_format_reference_set_expanded_view.tsv.gz';


COPY (
  SELECT
    concept.id,
    concept.effective_time,
    concept.active,
    concept.module_id,
    get_concept_preferred_term(concept.module_id) module_name,
    concept.definition_status_id,
    get_concept_preferred_term(concept.definition_status_id) definition_status_name,
    CASE WHEN concept.definition_status_id = 900000000000074008 THEN true ELSE false END AS is_primitive,
    get_concept_fully_specified_name(concept.id) fully_specified_name,
    get_concept_preferred_term(concept.id) preferred_term,
    array_to_json(ARRAY(SELECT term FROM denormalized_description_for_current_snapshot WHERE concept_id = concept.id AND type_id=900000000000550004)) AS definition,
    array_to_json(ARRAY(SELECT (des.id, des.type_id, des.type_name, des.term, des.case_significance_id, des.case_significance_name)::denormalized_description_type
        FROM denormalized_description_for_current_snapshot des
        JOIN current_language_reference_set_snapshot ref
        ON ref.referenced_component_id = des.id
        AND des.concept_id = concept.id
        AND des.active = true)) AS descriptions,
    array_to_json(extract_expanded_concepts_for_parents(concept.id)) parents,
    array_to_json(extract_expanded_concepts_for_children(concept.id)) children,
    array_to_json(extract_expanded_concepts_for_ancestors(concept.id)) ancestors,
    array_to_json(extract_expanded_concepts_for_descendants(concept.id)) descendants,
    array_to_json(ARRAY(
      SELECT (
        rel.id,
        rel.effective_time,
        rel.active,
        rel.module_id,
        rel.module_name,
        rel.relationship_group,
        rel.source_id,
        rel.source_name,
        rel.destination_id,
        rel.destination_name,
        rel.type_id,
        rel.type_name,
        rel.characteristic_type_id,
        rel.characteristic_type_name,
        rel.modifier_id,
        rel.modifier_name)::denormalized_relationship_type
      FROM snomed_denormalized_relationship_for_current_snapshot rel
      WHERE rel.destination_id = concept.id
      AND rel.active = true)) incoming_relationships,
    array_to_json(ARRAY(
      SELECT (
        rel.id,
        rel.effective_time,
        rel.active,
        rel.module_id,
        rel.module_name,
        rel.relationship_group,
        rel.source_id,
        rel.source_name,
        rel.destination_id,
        rel.destination_name,
        rel.type_id,
        rel.type_name,
        rel.characteristic_type_id,
        rel.characteristic_type_name,
        rel.modifier_id,
        rel.modifier_name)::denormalized_relationship_type
      FROM snomed_denormalized_relationship_for_current_snapshot rel
      WHERE rel.source_id = concept.id
      AND rel.active = true)) outgoing_relationships,
    array_to_json(ARRAY(
      SELECT (
        ref.refset_id,
        ref.refset_type)::denormalized_reference_set_identifier
      FROM snomed_denormalized_refset_view_for_current_snapshot ref
      WHERE referenced_component_id = concept.id)) reference_set_memberships
FROM current_concept_snapshot concept)  TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/snomed_denormalized_concept_view_for_current_snapshot.tsv.gz';


COPY (
  SELECT id,
  effective_time,
  active,
  module_id,
  module_name,
  relationship_group,
  source_id,
  source_name,
  destination_id,
  destination_name,
  type_id,
  type_name,
  characteristic_type_id,
  characteristic_type_name,
  modifier_id,
  modifier_name
  FROM snomed_denormalized_relationship_for_current_snapshot)
TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/snomed_denormalized_relationship_for_current_snapshot.tsv.gz';

COPY (
  SELECT
  subtype_id,
  supertype_id,
  effective_time,
  active
  FROM single_snapshot_transitive_closure)
TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/snomed_transitive_closure_for_current_snapshot.tsv.gz';

COPY (
  SELECT
  id,
  module_id,
  module_name,
  effective_time,
  language_code,
  active,
  type_id,
  type_name,
  term,
  case_significance_id,
  case_significance_name,
  concept_id,
  reference_set_memberships
  FROM denormalized_description_for_current_snapshot)
TO PROGRAM 'gzip > /opt/snomedct_buildserver/final_build_data/denormalized_description_for_current_snapshot.tsv.gz';

-- outputs a file with a single line that looks like:
-- snomed-20160131-release-server
COPY (
  SELECT
      concat('snomed-',
          replace(
              split_part(
                  trim(leading 'SNOMED Clinical Terms version:' from term),
                  '(', 1),
              ' [R]',
              '-release-server'))
  FROM current_description_snapshot
  WHERE concept_id = 138875005
  AND term LIKE '%SNOMED Clinical Terms version:%'
  AND active = true)
TO '/opt/snomedct_buildserver/final_build_data/current_version_info';
