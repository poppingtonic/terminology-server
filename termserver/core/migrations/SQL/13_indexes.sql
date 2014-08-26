CREATE INDEX concept_component_id_index ON snomed_concept(component_id);
CREATE INDEX description_component_id_index ON snomed_description(component_id);
CREATE INDEX description_concept_id_index ON snomed_description(concept_id);
CREATE INDEX source_id_index ON snomed_relationship(source_id);
CREATE INDEX destination_id_index ON snomed_relationship(destination_id);
CREATE INDEX con_composite ON snomed_concept(component_id, effective_time, active, module_id, definition_status_id);
CREATE INDEX lang_refset_referenced_component ON snomed_language_reference_set(referenced_component_id);
CREATE INDEX snomed_subsumption_concept_id ON snomed_subsumption(concept_id);
CREATE INDEX concept_expanded_view_concept_id ON concept_expanded_view(concept_id);
CREATE INDEX con_desc_cte_concept_id ON con_desc_cte(concept_id);
CREATE INDEX concept_preferred_terms_concept_id_term ON concept_preferred_terms(concept_id, preferred_term);
CREATE INDEX description_expanded_view_id ON description_expanded_view(id);
CREATE INDEX description_expanded_view_component_id ON description_expanded_view(component_id);
CREATE INDEX relationship_expanded_view_component_id ON relationship_expanded_view(component_id);
CREATE INDEX relationship_expanded_view_id ON relationship_expanded_view(id);


CREATE INDEX con_effective_time ON snomed_concept_full(effective_time, component_id);
CREATE INDEX desc_effective_time ON snomed_description_full(effective_time, component_id);
CREATE INDEX rel_effective_time ON snomed_relationship_full(effective_time, component_id);
