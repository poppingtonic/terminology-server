-- The final output view for concepts
CREATE MATERIALIZED VIEW concept_expanded_view AS
SELECT
    -- Straight forward retrieval from the pre-processed view
    con_desc.id, con_desc.concept_id, con_desc.effective_time, con_desc.active, con_desc.is_primitive,
    -- Look up the names of these attributes
    con_desc.module_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = con_desc.module_id) AS module_name,
    con_desc.definition_status_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = con_desc.definition_status_id) AS definition_status_name,
    -- Get the descriptions from the stored procedure
    processed_descriptions.descriptions, processed_descriptions.preferred_terms, processed_descriptions.synonyms,
    processed_descriptions.fully_specified_name, processed_descriptions.definition, processed_descriptions.preferred_term,
    -- Relationships - use stored procedure to fill out
    processed_rels.is_a_parents, processed_rels.is_a_children,
    processed_rels.is_a_direct_parents, processed_rels.is_a_direct_children,
    processed_rels.part_of_parents, processed_rels.part_of_children,
    processed_rels.part_of_direct_parents, processed_rels.part_of_direct_children,
    processed_rels.other_parents, processed_rels.other_children,
    processed_rels.other_direct_parents, processed_rels.other_direct_children
FROM con_desc_cte con_desc
LEFT JOIN snomed_subsumption sub ON sub.concept_id = con_desc.concept_id
LEFT JOIN LATERAL process_descriptions(con_desc.descs) processed_descriptions ON true
LEFT JOIN LATERAL process_relationships(sub.*) processed_rels ON true;
