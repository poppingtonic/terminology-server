CREATE MATERIALIZED VIEW current_concept_snapshot AS
  select c.* from curr_concept_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_concept_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_relationship_snapshot AS
  select c.* from curr_relationship_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_relationship_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_description_snapshot AS
  select c.* from curr_description_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_description_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_annotation_reference_set_snapshot AS
  select c.* from curr_annotationrefset_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_annotationrefset_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_association_reference_set_snapshot AS
  select c.* from curr_associationrefset_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_associationrefset_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_attribute_value_reference_set_snapshot AS
  select c.* from curr_attributevaluerefset_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_attributevaluerefset_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_complex_map_reference_set_snapshot AS
  select c.* from curr_complexmaprefset_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_complexmaprefset_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_description_format_reference_set_snapshot AS
  select c.* from curr_descriptionformatrefset_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_descriptionformatrefset_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_extended_map_reference_set_snapshot AS
  select c.* from curr_extendedmaprefset_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_extendedmaprefset_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_language_reference_set_snapshot AS
  select c.* from curr_langrefset_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_langrefset_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_module_dependency_reference_set_snapshot AS
  select c.* from curr_moduledependencyrefset_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_moduledependencyrefset_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_ordered_reference_set_snapshot AS
  select c.* from curr_orderedrefset_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_orderedrefset_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_query_specification_reference_set_snapshot AS
  select c.* from curr_queryspecificationrefset_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_queryspecificationrefset_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_reference_set_descriptor_reference_set_snapshot AS
  select c.* from curr_referencesetdescriptorrefset_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_referencesetdescriptorrefset_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_simple_map_reference_set_snapshot AS
  select c.* from curr_simplemaprefset_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_simplemaprefset_f c2
        where c2.id = c.id);

CREATE MATERIALIZED VIEW current_simple_reference_set_snapshot AS
  select c.* from curr_simplerefset_f as c
  where c.effective_time = (select max(c2.effective_time) from curr_simplerefset_f c2
        where c2.id = c.id);

CREATE INDEX description_index_type_id ON current_description_snapshot (type_id);
CREATE INDEX description_index_conceptid ON current_description_snapshot (concept_id);
CREATE INDEX description_partial_index_type_id_fsn ON current_description_snapshot (type_id) WHERE type_id = 900000000000003001;
CREATE INDEX concept_index_conceptid ON current_concept_snapshot (id);
CREATE INDEX langrefset_referencedcomponentid_index on current_language_reference_set_snapshot (referenced_component_id);
CREATE INDEX langrefset_partial_index_acceptability_id_pt ON current_language_reference_set_snapshot (acceptability_id) WHERE acceptability_id = 900000000000548007;
CREATE INDEX snomed_relationship_destination_id_index ON current_relationship_snapshot (destination_id);
CREATE INDEX snomed_relationship_sourceid_index ON current_relationship_snapshot (source_id);
