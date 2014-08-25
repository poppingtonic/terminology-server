CREATE MATERIALIZED VIEW snomed_annotation_reference_set AS
SELECT refset.* FROM snomed_annotation_reference_set_full refset
WHERE refset.effective_time =
    (SELECT MAX(rs.effective_time) FROM snomed_annotation_reference_set_full rs WHERE rs.id = refset.id);

CREATE MATERIALIZED VIEW snomed_association_reference_set AS
SELECT refset.* FROM snomed_association_reference_set_full refset
WHERE refset.effective_time =
    (SELECT MAX(rs.effective_time) FROM snomed_association_reference_set_full rs WHERE rs.id = refset.id);

CREATE MATERIALIZED VIEW snomed_attribute_value_reference_set AS
SELECT refset.* FROM snomed_attribute_value_reference_set_full refset
WHERE refset.effective_time =
    (SELECT MAX(rs.effective_time) FROM snomed_attribute_value_reference_set_full rs WHERE rs.id = refset.id);

CREATE MATERIALIZED VIEW snomed_complex_map_reference_set AS
SELECT refset.* FROM snomed_complex_map_reference_set_full refset
WHERE refset.effective_time =
    (SELECT MAX(rs.effective_time) FROM snomed_complex_map_reference_set_full rs WHERE rs.id = refset.id);

CREATE MATERIALIZED VIEW snomed_description_format_reference_set AS
SELECT refset.* FROM snomed_description_format_reference_set_full refset
WHERE refset.effective_time =
    (SELECT MAX(rs.effective_time) FROM snomed_description_format_reference_set_full rs WHERE rs.id = refset.id);

CREATE MATERIALIZED VIEW snomed_extended_map_reference_set AS
SELECT refset.* FROM snomed_extended_map_reference_set_full refset
WHERE refset.effective_time =
    (SELECT MAX(rs.effective_time) FROM snomed_extended_map_reference_set_full rs WHERE rs.id = refset.id);

CREATE MATERIALIZED VIEW snomed_language_reference_set AS
SELECT refset.* FROM snomed_language_reference_set_full refset
WHERE refset.effective_time =
    (SELECT MAX(rs.effective_time) FROM snomed_language_reference_set_full rs WHERE rs.id = refset.id);

CREATE MATERIALIZED VIEW snomed_module_dependency_reference_set AS
SELECT refset.* FROM snomed_module_dependency_reference_set_full refset
WHERE refset.effective_time =
    (SELECT MAX(rs.effective_time) FROM snomed_module_dependency_reference_set_full rs WHERE rs.id = refset.id);

CREATE MATERIALIZED VIEW snomed_ordered_reference_set AS
SELECT refset.* FROM snomed_ordered_reference_set_full refset
WHERE refset.effective_time =
    (SELECT MAX(rs.effective_time) FROM snomed_ordered_reference_set_full rs WHERE rs.id = refset.id);

CREATE MATERIALIZED VIEW snomed_query_specification_reference_set AS
SELECT refset.* FROM snomed_query_specification_reference_set_full refset
WHERE refset.effective_time =
    (SELECT MAX(rs.effective_time) FROM snomed_query_specification_reference_set_full rs WHERE rs.id = refset.id);

CREATE MATERIALIZED VIEW snomed_reference_set_descriptor_reference_set AS
SELECT refset.* FROM snomed_reference_set_descriptor_reference_set_full refset
WHERE refset.effective_time =
    (SELECT MAX(rs.effective_time) FROM snomed_reference_set_descriptor_reference_set_full rs WHERE rs.id = refset.id);

CREATE MATERIALIZED VIEW snomed_simple_map_reference_set AS
SELECT refset.* FROM snomed_simple_map_reference_set_full refset
WHERE refset.effective_time =
    (SELECT MAX(rs.effective_time) FROM snomed_simple_map_reference_set_full rs WHERE rs.id = refset.id);

CREATE MATERIALIZED VIEW snomed_simple_reference_set AS
SELECT refset.* FROM snomed_simple_reference_set_full refset
WHERE refset.effective_time =
    (SELECT MAX(rs.effective_time) FROM snomed_simple_reference_set_full rs WHERE rs.id = refset.id);
