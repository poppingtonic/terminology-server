# coding=utf-8
"""UNMANAGED models for MATERIALIZED VIEWS that are used as performance optimizations"""
from django.db import models
from jsonfield import JSONField


class ConceptView(models.Model):
    """
CREATE MATERIALIZED VIEW concept_expanded_view AS
SELECT
    -- Straight forward retrieval from the concept table
    con_desc.concept_id, con_desc.effective_time, con_desc.active, con_desc.module_id, con_desc.definition_status_id, con_desc.is_primitive,
    processed_descriptions.descriptions, processed_descriptions.preferred_terms, processed_descriptions.synonyms,
    processed_descriptions.fully_specified_name, processed_descriptions.definition, processed_descriptions.preferred_term,
    -- Relationships - add preferred term of referenced concepts
    process_relationships(sub.is_a_parents) AS is_a_parents,
    process_relationships(sub.is_a_children) AS is_a_children,
    process_relationships(sub.is_a_direct_parents) AS is_a_direct_parents,
    process_relationships(sub.is_a_direct_children) AS is_a_direct_children,
    process_relationships(sub.part_of_parents) AS part_of_parents,
    process_relationships(sub.part_of_children) AS part_of_children,
    process_relationships(sub.part_of_direct_parents) AS part_of_direct_parents,
    process_relationships(sub.part_of_direct_children) AS part_of_direct_children,
    process_relationships(sub.other_parents) AS other_parents,
    process_relationships(sub.other_children) AS other_children,
    process_relationships(sub.other_direct_parents) AS other_direct_parents,
    process_relationships(sub.other_direct_children) AS other_direct_children
FROM con_desc_cte con_desc
LEFT JOIN LATERAL process_descriptions(con_desc.descs) processed_descriptions ON true
LEFT JOIN snomed_subsumption sub ON sub.concept_id = con_desc.concept_id;
    """
    pass

    class Meta(object):
        managed = False


class DescriptionView(models.Model):
    """
    CREATE MATERIALIZED VIEW description_expanded_view AS
    SELECT
       descr.id, descr.component_id, descr.effective_time, descr.active, descr.language_code, descr.term,
       descr.module_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = descr.module_id) AS module_name,
       descr.concept_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = descr.concept_id) AS concept_name,
       descr.type_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = descr.type_id) AS type_name,
       descr.case_significance_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = descr.case_significance_id) AS case_significance_name
    FROM snomed_description descr;
    CREATE INDEX description_expanded_view_id ON description_expanded_view(id);
    CREATE INDEX description_expanded_view_component_id ON description_expanded_view(component_id);
    """
    pass

    class Meta(object):
        managed = False


class RelationshipView(models.Model):
    """
    CREATE MATERIALIZED VIEW relationship_expanded_view AS
    SELECT
      rel.id, rel.component_id, rel.effective_time, rel.active, rel.relationship_group,
      rel.module_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rel.module_id) AS module_name,
      rel.source_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rel.source_id) AS source_name,
      rel.destination_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rel.destination_id) AS destination_name,
      rel.type_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rel.type_id) AS type_name,
      rel.characteristic_type_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rel.characteristic_type_id) AS characteristic_type_name,
      rel.modifier_id, (SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = rel.modifier_id) AS modifier_name
    FROM snomed_relationship rel;
    """
    pass

    class Meta(object):
        managed = False


class SubsumptionView(models.Model):
    """This maps the view that pre-computes all subsumption information"""
    concept_id = models.BigIntegerField(editable=False)

    is_a_direct_parents = models.JSONField(editable=False)
    is_a_parents = models.JSONField(editable=False)
    is_a_direct_children = models.JSONField(editable=False)
    is_a_children = models.JSONField(editable=False)

    part_of_direct_parents = models.JSONField(editable=False)
    part_of_parents = models.JSONField(editable=False)
    part_of_direct_children = models.JSONField(editable=False)
    part_of_children = models.JSONField(editable=False)

    other_direct_parents = models.JSONField(editable=False)
    other_parents = models.JSONField(editable=False)
    other_direct_children = models.JSONField(editable=False)
    other_children = models.JSONField(editable=False)

    class Meta(object):
        managed = False
        db_table = 'snomed_subsumption'
