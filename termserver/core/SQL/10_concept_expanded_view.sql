-- The final output view for concepts
CREATE MATERIALIZED VIEW concept_expanded_view AS
SELECT
    -- Straight forward retrieval from the pre-processed view
    con_desc.id, con_desc.concept_id, con_desc.effective_time, con_desc.active, con_desc.is_primitive,
    -- Look up the names of these attributes
    con_desc.module_id, get_concept_preferred_term(con_desc.module_id) AS module_name,
    con_desc.definition_status_id, get_concept_preferred_term(con_desc.definition_status_id) AS definition_status_name,
    -- Get the descriptions from the stored procedure
    con_desc.descs as descriptions,
    extract_preferred_terms(con_desc.descs) as preferred_terms,
    extract_synonyms(con_desc.descs) as synonyms,
    extract_fully_specified_name(con_desc.descs) as fully_specified_name,
    extract_definition(con_desc.descs) as definition,
    extract_preferred_term(con_desc.descs) as preferred_term,
    -- Relationships - use stored procedure to fill out
    expand_relationships(sub.is_a_parents) as is_a_parents,
    expand_relationships(sub.is_a_children) as is_a_children,
    expand_relationships(sub.is_a_direct_parents) as is_a_direct_parents,
    expand_relationships(sub.is_a_direct_children) as is_a_direct_children,
    expand_relationships(sub.part_of_parents) as part_of_parents,
    expand_relationships(sub.part_of_children) as part_of_children,
    expand_relationships(sub.part_of_direct_parents) as part_of_direct_parents,
    expand_relationships(sub.part_of_direct_children) as part_of_direct_children,
    expand_relationships(sub.other_parents) as other_parents,
    expand_relationships(sub.other_children) as other_children,
    expand_relationships(sub.other_direct_parents) as other_direct_parents,
    expand_relationships(sub.other_direct_children) as other_direct_children
FROM con_desc_cte con_desc
JOIN snomed_subsumption sub ON sub.concept_id = con_desc.concept_id;
