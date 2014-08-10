# coding=utf-8
"""Haystack search mapping"""
from haystack import indexes
from core.models import ConceptView


class ConceptIndex(indexes.SearchIndex, indexes.Indexable):
    """Index concepts and their associated descriptions / relationships"""
    # These identify individual documents
    id = indexes.IntegerField(indexed=False)
    concept_id = indexes.IntegerField(indexed=False)

    # These will be used to filter and facet
    effective_time = indexes.FacetDateField()
    active = indexes.FacetBooleanField()
    is_primitive = indexes.FacetBooleanField()
    module_id = indexes.FacetIntegerField()
    definition_status_id = indexes.FacetIntegerField()
    is_a_parents = indexes.FacetMultiValueField(model_attr='is_a_parents_ids')
    is_a_children = indexes.FacetMultiValueField(model_attr='is_a_children_ids')

    # These are the actual search fields
    text = indexes.CharField(document=True, use_template=False, model_attr='descriptions_list')
    text_autocomplete = indexes.EdgeNgramField(model_attr='descriptions_list')
    definition_status_name = indexes.CharField()
    module_name = indexes.CharField()
    fully_specified_name = indexes.CharField()
    preferred_term = indexes.CharField()

    def get_model(self):
        """Use the pre-computed concept view; all the necessary information is already inlined"""
        return ConceptView

    def index_queryset(self, using=None):
        """Index every entry in the concept view"""
        return self.get_model().objects.all()
