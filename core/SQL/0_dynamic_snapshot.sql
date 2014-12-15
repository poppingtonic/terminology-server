CREATE VIEW snomed_concept AS
WITH recent_view_cte AS (
    SELECT component_id, MAX(effective_time) AS max_effective_time
    FROM snomed_concept_full
    GROUP BY component_id
)
SELECT component.*
FROM snomed_concept_full component
JOIN recent_view_cte ON
    component.component_id = recent_view_cte.component_id
    AND component.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_description AS
WITH recent_view_cte AS (
    SELECT component_id, MAX(effective_time) AS max_effective_time
    FROM snomed_description_full
    GROUP BY component_id
)
SELECT component.*
FROM snomed_description_full component
JOIN recent_view_cte ON
    component.component_id = recent_view_cte.component_id
    AND component.effective_time = recent_view_cte.max_effective_time;

CREATE VIEW snomed_relationship AS
WITH recent_view_cte AS (
    SELECT component_id, MAX(effective_time) AS max_effective_time
    FROM snomed_relationship_full
    GROUP BY component_id
)
SELECT component.*
FROM snomed_relationship_full component
JOIN recent_view_cte ON
    component.component_id = recent_view_cte.component_id
    AND component.effective_time = recent_view_cte.max_effective_time;
