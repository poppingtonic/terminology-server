CREATE VIEW snomed_annotation_reference_set AS
WITH recent_view_cte AS (
    SELECT row_id, MAX(effective_time) AS max_effective_time
    FROM snomed_annotation_reference_set_full
    GROUP BY row_id
)
SELECT refset.*
FROM snomed_annotation_reference_set_full refset
JOIN recent_view_cte ON
    refset.row_id = recent_view_cte.row_id
    AND refset.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_association_reference_set AS
WITH recent_view_cte AS (
    SELECT row_id, MAX(effective_time) AS max_effective_time
    FROM snomed_association_reference_set_full
    GROUP BY row_id
)
SELECT refset.*
FROM snomed_association_reference_set_full refset
JOIN recent_view_cte ON
    refset.row_id = recent_view_cte.row_id
    AND refset.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_attribute_value_reference_set AS
WITH recent_view_cte AS (
    SELECT row_id, MAX(effective_time) AS max_effective_time
    FROM snomed_attribute_value_reference_set_full
    GROUP BY row_id
)
SELECT refset.*
FROM snomed_attribute_value_reference_set_full refset
JOIN recent_view_cte ON
    refset.row_id = recent_view_cte.row_id
    AND refset.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_complex_map_reference_set AS
WITH recent_view_cte AS (
    SELECT row_id, MAX(effective_time) AS max_effective_time
    FROM snomed_complex_map_reference_set_full
    GROUP BY row_id
)
SELECT refset.*
FROM snomed_complex_map_reference_set_full refset
JOIN recent_view_cte ON
    refset.row_id = recent_view_cte.row_id
    AND refset.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_description_format_reference_set AS
WITH recent_view_cte AS (
    SELECT row_id, MAX(effective_time) AS max_effective_time
    FROM snomed_description_format_reference_set_full
    GROUP BY row_id
)
SELECT refset.*
FROM snomed_description_format_reference_set_full refset
JOIN recent_view_cte ON
    refset.row_id = recent_view_cte.row_id
    AND refset.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_extended_map_reference_set AS
WITH recent_view_cte AS (
    SELECT row_id, MAX(effective_time) AS max_effective_time
    FROM snomed_extended_map_reference_set_full
    GROUP BY row_id
)
SELECT refset.*
FROM snomed_extended_map_reference_set_full refset
JOIN recent_view_cte ON
    refset.row_id = recent_view_cte.row_id
    AND refset.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_language_reference_set AS
WITH recent_view_cte AS (
    SELECT row_id, MAX(effective_time) AS max_effective_time
    FROM snomed_language_reference_set_full
    GROUP BY row_id
)
SELECT refset.*
FROM snomed_language_reference_set_full refset
JOIN recent_view_cte ON
    refset.row_id = recent_view_cte.row_id
    AND refset.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_module_dependency_reference_set AS
WITH recent_view_cte AS (
    SELECT row_id, MAX(effective_time) AS max_effective_time
    FROM snomed_module_dependency_reference_set_full
    GROUP BY row_id
)
SELECT refset.*
FROM snomed_module_dependency_reference_set_full refset
JOIN recent_view_cte ON
    refset.row_id = recent_view_cte.row_id
    AND refset.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_ordered_reference_set AS
WITH recent_view_cte AS (
    SELECT row_id, MAX(effective_time) AS max_effective_time
    FROM snomed_ordered_reference_set_full
    GROUP BY row_id
)
SELECT refset.*
FROM snomed_ordered_reference_set_full refset
JOIN recent_view_cte ON
    refset.row_id = recent_view_cte.row_id
    AND refset.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_query_specification_reference_set AS
WITH recent_view_cte AS (
    SELECT row_id, MAX(effective_time) AS max_effective_time
    FROM snomed_query_specification_reference_set_full
    GROUP BY row_id
)
SELECT refset.*
FROM snomed_query_specification_reference_set_full refset
JOIN recent_view_cte ON
    refset.row_id = recent_view_cte.row_id
    AND refset.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_reference_set_descriptor_reference_set AS
WITH recent_view_cte AS (
    SELECT row_id, MAX(effective_time) AS max_effective_time
    FROM snomed_reference_set_descriptor_reference_set_full
    GROUP BY row_id
)
SELECT refset.*
FROM snomed_reference_set_descriptor_reference_set_full refset
JOIN recent_view_cte ON
    refset.row_id = recent_view_cte.row_id
    AND refset.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_simple_map_reference_set AS
WITH recent_view_cte AS (
    SELECT row_id, MAX(effective_time) AS max_effective_time
    FROM snomed_simple_map_reference_set_full
    GROUP BY row_id
)
SELECT refset.*
FROM snomed_simple_map_reference_set_full refset
JOIN recent_view_cte ON
    refset.row_id = recent_view_cte.row_id
    AND refset.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_simple_reference_set AS
WITH recent_view_cte AS (
    SELECT row_id, MAX(effective_time) AS max_effective_time
    FROM snomed_simple_reference_set_full
    GROUP BY row_id
)
SELECT refset.*
FROM snomed_simple_reference_set_full refset
JOIN recent_view_cte ON
    refset.row_id = recent_view_cte.row_id
    AND refset.effective_time = recent_view_cte.max_effective_time;
