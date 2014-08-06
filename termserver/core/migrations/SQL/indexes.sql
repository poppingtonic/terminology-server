CREATE INDEX concept_component_id_index ON snomed_concept(component_id);
CREATE INDEX description_component_id_index ON snomed_description(component_id);
CREATE INDEX description_concept_id_index ON snomed_description(concept_id);
CREATE INDEX source_id_index ON snomed_relationship(source_id);
CREATE INDEX destination_id_index ON snomed_relationship(destination_id);
CREATE INDEX lang_refset_referenced_component ON snomed_language_reference_set(referenced_component_id);
CREATE INDEX con_composite ON snomed_concept(component_id, effective_time, active, module_id, definition_status_id);
