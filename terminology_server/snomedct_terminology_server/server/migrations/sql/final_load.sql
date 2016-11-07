CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE LANGUAGE plpythonu;

-- Concatenates the referenced_component_name and refset_name field, then returns a tsvector. Immutable due to indexing.
CREATE OR REPLACE FUNCTION combined_field_tsvector(r_name text, rc_name text) RETURNS tsvector AS $combined$
BEGIN
   RETURN to_tsvector('english', concat_ws(' ', r_name, rc_name));
END;
$combined$
LANGUAGE plpgsql IMMUTABLE;

COPY language_reference_set_expanded_view(
 id, effective_time, active,
 module_id, module_name,
 refset_id, refset_name,
 referenced_component_id, referenced_component_name,
 acceptability_id, acceptability_name)
 FROM '/opt/snomedct_terminology_server/final_build_data/language_reference_set_expanded_view.tsv';

COPY reference_set_descriptor_reference_set_expanded_view(
 id, effective_time, active,
 module_id, module_name,
 refset_id, refset_name,
 referenced_component_id, referenced_component_name,
 attribute_description_id, attribute_description_name,
 attribute_type_id, attribute_type_name, attribute_order
)
FROM '/opt/snomedct_terminology_server/final_build_data/reference_set_descriptor_reference_set_expanded_view.tsv';

COPY simple_reference_set_expanded_view(
 id, effective_time, active,
 module_id, module_name,
 refset_id, refset_name,
 referenced_component_id, referenced_component_name
) FROM '/opt/snomedct_terminology_server/final_build_data/simple_reference_set_expanded_view.tsv';

COPY ordered_reference_set_expanded_view(
 id, effective_time, active, "order",
 module_id, module_name,
 refset_id, refset_name,
 referenced_component_id, referenced_component_name,
 linked_to_id, linked_to_name
) FROM '/opt/snomedct_terminology_server/final_build_data/ordered_reference_set_expanded_view.tsv';

COPY attribute_value_reference_set_expanded_view(
 id, effective_time, active,
 module_id, module_name,
 refset_id, refset_name,
 referenced_component_id, referenced_component_name,
 value_id, value_name
) FROM '/opt/snomedct_terminology_server/final_build_data/attribute_value_reference_set_expanded_view.tsv';

COPY simple_map_reference_set_expanded_view(
 id, effective_time, active,
 module_id, module_name,
 refset_id, refset_name,
 referenced_component_id, referenced_component_name,
 map_target
) FROM '/opt/snomedct_terminology_server/final_build_data/simple_map_reference_set_expanded_view.tsv';

COPY complex_map_reference_set_expanded_view(
 id, effective_time, active,
 module_id, module_name,
 refset_id, refset_name,
 referenced_component_id, referenced_component_name,
 correlation_id, correlation_name,
 map_group, map_priority, map_rule, map_advice, map_target, map_block
) FROM '/opt/snomedct_terminology_server/final_build_data/complex_map_reference_set_expanded_view.tsv';

COPY extended_map_reference_set_expanded_view(
 id, effective_time, active,
 module_id, module_name,
 refset_id, refset_name,
 referenced_component_id, referenced_component_name,
 correlation_id, correlation_name,
 map_category_id, map_category_name,
 map_group, map_priority, map_rule, map_advice, map_target
) FROM '/opt/snomedct_terminology_server/final_build_data/extended_map_reference_set_expanded_view.tsv';

COPY query_specification_reference_set_expanded_view(
 id, effective_time, active,
 module_id, module_name,
 refset_id, refset_name,
 referenced_component_id, referenced_component_name,
 query
) FROM '/opt/snomedct_terminology_server/final_build_data/query_specification_reference_set_expanded_view.tsv';

COPY annotation_reference_set_expanded_view(
 id, effective_time, active,
 module_id, module_name,
 refset_id, refset_name,
 referenced_component_id, referenced_component_name, annotation
) FROM '/opt/snomedct_terminology_server/final_build_data/annotation_reference_set_expanded_view.tsv';

COPY association_reference_set_expanded_view(
 id, effective_time, active,
 module_id, module_name,
 refset_id, refset_name,
 referenced_component_id, referenced_component_name,
 target_component_id, target_component_name
) FROM '/opt/snomedct_terminology_server/final_build_data/association_reference_set_expanded_view.tsv';

COPY module_dependency_reference_set_expanded_view(
 id, effective_time, active,
 module_id, module_name,
 refset_id, refset_name,
 referenced_component_id, referenced_component_name,
 source_effective_time, target_effective_time
) FROM '/opt/snomedct_terminology_server/final_build_data/module_dependency_reference_set_expanded_view.tsv';

COPY description_format_reference_set_expanded_view(
 id, effective_time, active,
 module_id, module_name,
 refset_id, refset_name,
 referenced_component_id, referenced_component_name,
 description_format_id, description_format_name, description_length
) FROM '/opt/snomedct_terminology_server/final_build_data/description_format_reference_set_expanded_view.tsv';

COPY denormalized_description_for_current_snapshot(id, module_id, module_name, effective_time, language_code, active, type_id, type_name, term, case_significance_id, case_significance_name, concept_id, reference_set_memberships)
FROM '/opt/snomedct_terminology_server/final_build_data/denormalized_description_for_current_snapshot.tsv'
WITH (FORMAT text);

COPY transitive_closure_for_current_snapshot(subtype_id, supertype_id, effective_time, active)
FROM '/opt/snomedct_terminology_server/final_build_data/snomed_transitive_closure_for_current_snapshot.tsv'
WITH (FORMAT text);

COPY denormalized_relationship_for_current_snapshot(id,  effective_time, active, module_id, module_name, relationship_group, source_id, source_name, destination_id, destination_name, type_id, type_name, characteristic_type_id, characteristic_type_name, modifier_id, modifier_name)
FROM '/opt/snomedct_terminology_server/final_build_data/snomed_denormalized_relationship_for_current_snapshot.tsv'
WITH (FORMAT text);

COPY snomed_denormalized_concept_view_for_current_snapshot(id, effective_time, active, module_id, module_name, definition_status_id, definition_status_name, is_primitive, fully_specified_name, preferred_term, definition, descriptions, descriptions_tsvector, parents, children, ancestors, descendants, incoming_relationships, outgoing_relationships, reference_set_memberships)
FROM '/opt/snomedct_terminology_server/final_build_data/snomed_denormalized_concept_view_for_current_snapshot.tsv'
WITH (FORMAT text);

CREATE UNIQUE INDEX language_reference_set_expanded_view_id ON language_reference_set_expanded_view(id);
CREATE INDEX language_reference_set_expanded_view_referenced_component_id ON language_reference_set_expanded_view(referenced_component_id);
CREATE INDEX language_reference_set_expanded_view_refset_id ON language_reference_set_expanded_view(refset_id);
CREATE INDEX language_reference_set_expanded_view_text ON language_reference_set_expanded_view USING gin (combined_field_tsvector(refset_name, referenced_component_name));

CREATE UNIQUE INDEX reference_set_descriptor_reference_set_expanded_view_id ON reference_set_descriptor_reference_set_expanded_view(id);
CREATE INDEX reference_set_descriptor_reference_set_expanded_view_referenced_component_id ON reference_set_descriptor_reference_set_expanded_view(referenced_component_id);
CREATE INDEX reference_set_descriptor_reference_set_expanded_view_refset_id ON reference_set_descriptor_reference_set_expanded_view(refset_id);
CREATE INDEX reference_set_descriptor_reference_set_text ON reference_set_descriptor_reference_set_expanded_view USING gin (combined_field_tsvector(refset_name, referenced_component_name));

CREATE UNIQUE INDEX simple_reference_set_expanded_view_id ON simple_reference_set_expanded_view(id);
CREATE INDEX simple_reference_set_expanded_view_referenced_component_id ON simple_reference_set_expanded_view(referenced_component_id);
CREATE INDEX simple_reference_set_expanded_view_refset_id ON simple_reference_set_expanded_view(refset_id);
CREATE INDEX simple_reference_set_expanded_view_text ON simple_reference_set_expanded_view USING gin (combined_field_tsvector(refset_name, referenced_component_name));

CREATE UNIQUE INDEX ordered_reference_set_expanded_view_id ON ordered_reference_set_expanded_view(id);
CREATE INDEX ordered_reference_set_expanded_view_referenced_component_id ON ordered_reference_set_expanded_view(referenced_component_id);
CREATE INDEX ordered_reference_set_expanded_view_refset_id ON ordered_reference_set_expanded_view(refset_id);
CREATE INDEX ordered_reference_set_text ON ordered_reference_set_expanded_view USING gin (combined_field_tsvector(refset_name, referenced_component_name));

CREATE UNIQUE INDEX attribute_value_reference_set_expanded_view_id ON attribute_value_reference_set_expanded_view(id);
CREATE INDEX attribute_value_reference_set_expanded_view_referenced_component_id ON attribute_value_reference_set_expanded_view(referenced_component_id);
CREATE INDEX attribute_value_reference_set_expanded_view_refset_id ON attribute_value_reference_set_expanded_view(refset_id);
CREATE INDEX attribute_value_reference_set_text ON attribute_value_reference_set_expanded_view USING gin (combined_field_tsvector(refset_name, referenced_component_name));

CREATE UNIQUE INDEX simple_map_reference_set_expanded_view_id ON simple_map_reference_set_expanded_view(id);
CREATE INDEX simple_map_reference_set_expanded_view_referenced_component_id ON simple_map_reference_set_expanded_view(referenced_component_id);
CREATE INDEX simple_map_reference_set_expanded_view_refset_id ON simple_map_reference_set_expanded_view(refset_id);
CREATE INDEX simple_map_reference_set_text ON simple_map_reference_set_expanded_view USING gin (combined_field_tsvector(refset_name, referenced_component_name));

CREATE UNIQUE INDEX complex_map_reference_set_expanded_view_id ON complex_map_reference_set_expanded_view(id);
CREATE INDEX complex_map_reference_set_expanded_view_referenced_component_id ON complex_map_reference_set_expanded_view(referenced_component_id);
CREATE INDEX complex_map_reference_set_expanded_view_refset_id ON complex_map_reference_set_expanded_view(refset_id);

CREATE UNIQUE INDEX extended_map_reference_set_expanded_view_id ON extended_map_reference_set_expanded_view(id);
CREATE INDEX extended_map_reference_set_expanded_view_referenced_component_id ON extended_map_reference_set_expanded_view(referenced_component_id);
CREATE INDEX extended_map_reference_set_expanded_view_refset_id ON extended_map_reference_set_expanded_view(refset_id);
CREATE INDEX extended_map_reference_set_text ON extended_map_reference_set_expanded_view USING gin (combined_field_tsvector(refset_name, referenced_component_name));

CREATE UNIQUE INDEX query_specification_reference_set_expanded_view_id ON query_specification_reference_set_expanded_view(id);
CREATE INDEX query_specification_reference_set_expanded_view_referenced_component_id ON query_specification_reference_set_expanded_view(referenced_component_id);
CREATE INDEX query_specification_reference_set_expanded_view_refset_id ON query_specification_reference_set_expanded_view(refset_id);
CREATE INDEX query_specification_reference_set_text ON query_specification_reference_set_expanded_view USING gin (combined_field_tsvector(refset_name, referenced_component_name));

CREATE UNIQUE INDEX annotation_reference_set_expanded_view_id ON annotation_reference_set_expanded_view(id);
CREATE INDEX annotation_reference_set_expanded_view_referenced_component_id ON annotation_reference_set_expanded_view(referenced_component_id);
CREATE INDEX annotation_reference_set_expanded_view_refset_id ON annotation_reference_set_expanded_view(refset_id);
CREATE INDEX annotation_reference_set_text ON annotation_reference_set_expanded_view USING gin (combined_field_tsvector(refset_name, referenced_component_name));

CREATE UNIQUE INDEX association_reference_set_expanded_view_id ON association_reference_set_expanded_view(id);
CREATE INDEX association_reference_set_expanded_view_referenced_component_id ON association_reference_set_expanded_view(referenced_component_id);
CREATE INDEX association_reference_set_expanded_view_refset_id ON association_reference_set_expanded_view(refset_id);
CREATE INDEX association_reference_set_text ON association_reference_set_expanded_view USING gin (combined_field_tsvector(refset_name, referenced_component_name));

CREATE UNIQUE INDEX module_dependency_reference_set_expanded_view_id ON module_dependency_reference_set_expanded_view(id);
CREATE INDEX module_dependency_reference_set_expanded_view_referenced_component_id ON module_dependency_reference_set_expanded_view(referenced_component_id);
CREATE INDEX module_dependency_reference_set_expanded_view_refset_id ON module_dependency_reference_set_expanded_view(refset_id);
CREATE INDEX module_dependency_reference_set_text ON module_dependency_reference_set_expanded_view USING gin (combined_field_tsvector(refset_name, referenced_component_name));

CREATE UNIQUE INDEX description_format_reference_set_expanded_view_id ON description_format_reference_set_expanded_view(id);
CREATE INDEX description_format_reference_set_expanded_view_referenced_component_id ON description_format_reference_set_expanded_view(referenced_component_id);
CREATE INDEX description_format_reference_set_expanded_view_refset_id ON description_format_reference_set_expanded_view(refset_id);
CREATE INDEX description_format_reference_set_text ON description_format_reference_set_expanded_view USING gin (combined_field_tsvector(refset_name, referenced_component_name));

CREATE INDEX fsn_denormalized_description_for_current_snapshot_type_id ON denormalized_description_for_current_snapshot (type_id) WHERE type_id = 900000000000003001;
CREATE INDEX ix_denormalized_description_for_current_snapshot_concept_id ON denormalized_description_for_current_snapshot (concept_id);
CREATE INDEX ix_denormalized_description_for_current_snapshot_id ON denormalized_description_for_current_snapshot (id);
CREATE INDEX ix_denormalized_description_for_current_snapshot_type_id ON denormalized_description_for_current_snapshot (type_id);

CREATE INDEX ix_tc_main ON  transitive_closure_for_current_snapshot (subtype_id,supertype_id);
CREATE INDEX ix_tc_inv ON  transitive_closure_for_current_snapshot (supertype_id);

CREATE INDEX ix_denormalized_relationship_id ON denormalized_relationship_for_current_snapshot (id);
CREATE INDEX ix_denormalized_relationship_type_id_partial ON denormalized_relationship_for_current_snapshot (type_id) WHERE type_id = 116680003;
CREATE INDEX ix_denormalized_relationship_defining ON denormalized_relationship_for_current_snapshot (characteristic_type_id, source_id) WHERE characteristic_type_id = 900000000000011006;
CREATE INDEX ix_denormalized_relationship_allowable_qualifiers ON denormalized_relationship_for_current_snapshot (characteristic_type_id, source_id) WHERE characteristic_type_id = 900000000000225001;
CREATE INDEX denormalized_relationship_active_destination_id ON denormalized_relationship_for_current_snapshot (destination_id, active);
CREATE INDEX denormalized_relationship_active_source_id ON denormalized_relationship_for_current_snapshot (source_id, active);

CREATE INDEX ix_denormalized_concept_id ON snomed_denormalized_concept_view_for_current_snapshot (id);
CREATE INDEX gist_denormalized_concept_fsn ON snomed_denormalized_concept_view_for_current_snapshot USING gist (fully_specified_name gist_trgm_ops);
CREATE INDEX gist_denormalized_concept_preferred_term ON snomed_denormalized_concept_view_for_current_snapshot USING gist (preferred_term gist_trgm_ops);
CREATE INDEX brin_denormalized_concept_effective_time ON snomed_denormalized_concept_view_for_current_snapshot USING brin (effective_time);
CREATE INDEX gin_descriptions_tsvector_ix ON snomed_denormalized_concept_view_for_current_snapshot USING gin (descriptions_tsvector);


CREATE OR REPLACE FUNCTION get_ids_from_jsonb(obj jsonb, field_name text) RETURNS bigint[] AS $$
DECLARE
   ids bigint[];
BEGIN
   ids := array(select jsonb_extract_path(jsonb_array_elements(obj), field_name));
   return ids;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

CREATE INDEX gin_jsonb_parent_ids ON snomed_denormalized_concept_view_for_current_snapshot USING gin (get_ids_from_jsonb(parents, 'concept_id'));

CREATE INDEX gin_jsonb_children_ids ON snomed_denormalized_concept_view_for_current_snapshot USING gin (get_ids_from_jsonb(children, 'concept_id'));

CREATE INDEX gin_jsonb_ancestor_ids ON snomed_denormalized_concept_view_for_current_snapshot USING gin (get_ids_from_jsonb(ancestors, 'concept_id'));

CREATE INDEX gin_jsonb_descendant_ids ON snomed_denormalized_concept_view_for_current_snapshot USING gin (get_ids_from_jsonb(descendants, 'concept_id'));

CREATE INDEX gin_jsonb_refset_membership_ids ON snomed_denormalized_concept_view_for_current_snapshot USING gin (get_ids_from_jsonb(reference_set_memberships, 'refset_id'));

CREATE MATERIALIZED VIEW has_amp_destination_ids AS
	SELECT json_object(array_agg(source_id::text), array_agg(destination_id::text)) has_amp
	FROM denormalized_relationship_for_current_snapshot
	WHERE type_id = 10362701000001108 AND active = true;

CREATE MATERIALIZED VIEW has_vmp_destination_ids AS
	SELECT json_object(array_agg(source_id::text), array_agg(destination_id::text)) has_vmp
	FROM denormalized_relationship_for_current_snapshot
	WHERE type_id = 10362601000001103 AND active = true;

CREATE MATERIALIZED VIEW has_dose_form_destination_ids AS
	SELECT json_object(array_agg(source_id::text), array_agg(destination_id::text)) has_dose_form
	FROM denormalized_relationship_for_current_snapshot
	WHERE type_id = 411116001 AND active = true;
