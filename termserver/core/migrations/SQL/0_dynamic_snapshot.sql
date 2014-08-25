CREATE MATERIALIZED VIEW snomed_concept AS
SELECT component.* FROM snomed_concept_full component
WHERE component.effective_time =
    (SELECT MAX(comp.effective_time) FROM snomed_concept_full comp WHERE comp.id = component.id);

CREATE MATERIALIZED VIEW snomed_description AS
SELECT component.* FROM snomed_description_full component
WHERE component.effective_time =
    (SELECT MAX(comp.effective_time) FROM snomed_description_full comp WHERE comp.id = component.id);

CREATE MATERIALIZED VIEW snomed_relationship AS
SELECT component.* FROM snomed_relationship_full component
WHERE component.effective_time =
    (SELECT MAX(comp.effective_time) FROM snomed_relationship_full comp WHERE comp.id = component.id);
