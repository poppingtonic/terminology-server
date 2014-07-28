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
    """This maps the materialized view that pre-computes the names of description attributes"""
    id = models.IntegerField(editable=False, primary_key=True)
    component_id = models.BigIntegerField(editable=False)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False)
    language_code = models.CharField(max_length=2, editable=False)
    term = models.TextField(editable=False)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    concept_id = models.BigIntegerField(editable=False)
    concept_name = models.TextField(editable=False)

    type_id = models.BigIntegerField(editable=False)
    type_name = models.TextField(editable=False)

    case_significance_id = models.BigIntegerField(editable=False)
    case_significance_name = models.TextField(editable=False)

    class Meta(object):
        managed = False
        db_table = 'description_expanded_view'


class RelationshipView(models.Model):
    """This maps the materialized view that pre-computes the names of relationship attributes"""
    id = models.IntegerField(editable=False, primary_key=True)
    component_id = models.BigIntegerField(editable=False)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False)
    relationship_group = models.SmallIntegerField(editable=False, null=True, blank=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    source_id = models.BigIntegerField(editable=False)
    source_name = models.TextField(editable=False)

    destination_id = models.BigIntegerField(editable=False)
    destination_name = models.TextField(editable=False)

    type_id = models.BigIntegerField(editable=False)
    type_name = models.TextField(editable=False)

    characteristic_type_id = models.BigIntegerField(editable=False)
    characteristic_type_name = models.TextField(editable=False)

    modifier_id = models.BigIntegerField(editable=False)
    modifier_name = models.TextField(editable=False)

    class Meta(object):
        managed = False
        db_table = 'relationship_expanded_view'


class SubsumptionView(models.Model):
    """This maps the materialized view that pre-computes all subsumption information"""
    concept_id = models.BigIntegerField(editable=False, primary_key=True)

    is_a_direct_parents = JSONField(editable=False)
    is_a_parents = JSONField(editable=False)
    is_a_direct_children = JSONField(editable=False)
    is_a_children = JSONField(editable=False)

    part_of_direct_parents = JSONField(editable=False)
    part_of_parents = JSONField(editable=False)
    part_of_direct_children = JSONField(editable=False)
    part_of_children = JSONField(editable=False)

    other_direct_parents = JSONField(editable=False)
    other_parents = JSONField(editable=False)
    other_direct_children = JSONField(editable=False)
    other_children = JSONField(editable=False)

    class Meta(object):
        managed = False
        db_table = 'snomed_subsumption'
