import six
from itertools import chain
from django.db import models
from stop_words import get_stop_words
from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.postgres.search import SearchRank, SearchVectorField
from rest_framework.exceptions import APIException
from snomedct_terminology_server.server.search import (PrefixMatchSearchQuery,
                                                       WordEquivalentMixin)
from snomedct_terminology_server.server.utils import (execute_query,
                                                      replace_all_measurement_units)


class SearchManager(models.Manager, WordEquivalentMixin):
    """This is a model manager with an analysis pipeline that includes
stopword removal, and autocorrection of input terms using the
'correct(text)' stored procedure. It does relevance ranking and
annotates the resultant queryset, which is required for doing an
order_by in core_views.py (ListConcepts).

    """
    # The URL query parameter used for the search.
    search_param = 'search'
    autocorrect_param = 'correct'
    synonyms_param = 'synonyms'

    def get_search_terms(self, request):
        """Search terms are set by a ?search=... query parameter, and may be
        comma and/or whitespace delimited. We use two optional filters:
        ?correct={true,false} and ?synonyms={true,false} to run
        autocorrect and to expand search terms with synonyms from the
        WordEquivalents table, respectively.

        """
        query_values = request.query_params.get(self.search_param, '')
        auto_correct = request.query_params.get(self.autocorrect_param, False)
        synonyms = request.query_params.get(self.synonyms_param, False)

        english_stop_words = get_stop_words('en')

        search_query_terms = query_values.replace(',', ' ')

        cleaned_up_terms = replace_all_measurement_units(search_query_terms)

        # clean up input terms, removing all tsquery syntax by using
        # to_tsvector with a simple configuration.
        terms = execute_query("select strip(to_tsvector('simple', %s))",
                              cleaned_up_terms).strip("'").split("\' \'")

        # only be forgiving for terms longer than 5 characters.
        if auto_correct:
            long_search_terms = [execute_query("select correct(%s)", word)
                                 for word in terms
                                 if word not in english_stop_words
                                 and len(word) > 5]

            short_search_terms = [word for word in terms
                                  if word not in english_stop_words
                                  and len(word) <= 5
                                  and len(word) > 0]
            terms = long_search_terms + short_search_terms

        if synonyms:
            word_equivalents = [self.get_word_equivalents(term)
                                for term in terms]
            terms = list(chain.from_iterable(word_equivalents))
        return terms

        search_query = WordEquivalentMixin().construct_tsquery_param(search_terms,
                                                                     search_modes[search_mode])

        required_fields = ', '.join(required_fields)

        select_expression = """SELECT {}, rank
FROM (SELECT {}, ts_rank(descriptions_tsvector, query) AS rank
FROM snomed_denormalized_concept_view_for_current_snapshot, tsq
WHERE active = true
AND descriptions_tsvector @@ query = true
{}) matches
ORDER BY rank DESC LIMIT 25""".format(required_fields,
                                      required_fields,
                                      facet_query_expression)

        full_cte_expression = """
WITH tsq AS (SELECT to_tsquery(%s) AS query) {}""".format(select_expression)

        raw_queryset = self.raw(full_cte_expression, [search_query])

        return raw_queryset

    def raw_search(self, request, queryset, required_fields, facet=None):
        UNSUPPORTED_API_EXCEPTION = """\
This search endpoint only supports the drug hierarchy, so please use the following endpoints:\
 '/terminology/concepts/search/amp', '/terminology/concepts/search/vmp' and \
'/terminology/concepts/search/drugs'"""

        facet_hierarchy = {
            'ancestor_ids.amp': '10363901000001102',
            'parents.ampp': '10364001000001104',
            'ancestor_ids.vmp': '10363801000001108',
            'parents.vtm': '10363701000001104',
            'parents.vmpp': '8653601000001108',
            'ancestor_ids.drugs': '373873005,115668003,410942007'
        }

        facet_template = "AND {} && ARRAY[%s]"

        if facet:
            try:
                assert facet in ('ancestor_ids.amp',
                                 'ancestor_ids.vmp',
                                 'ancestor_ids.drugs')
            except:
                raise APIException(detail=UNSUPPORTED_API_EXCEPTION)

            param = facet.split('.')[0]
            facet_query = facet_template.format(param)
            relatives = [int(rel) for rel in facet_hierarchy[facet].split(',')]
            concept_id_list = ', '.join(['%s::bigint']*len(relatives)) % tuple(relatives)
            facet_query_expression = facet_query % concept_id_list
        else:
            raise APIException(detail=UNSUPPORTED_API_EXCEPTION)

        search_terms = self.get_search_terms(request)

        search_query = WordEquivalentMixin().construct_tsquery_param(search_terms)

        required_fields = ', '.join(required_fields)

        search_query = PrefixMatchSearchQuery(search_terms)

        rank = SearchRank(vector, search_query)

        query = models.Q(**{orm_lookup: search_query})

        queryset = queryset.filter(query).annotate(rank=rank)
        return queryset

    def get_queryset(self):
        queryset = super(SearchManager, self).get_queryset()
        return queryset


class Concept(models.Model):
    class Meta:
        db_table = 'snomed_denormalized_concept_view_for_current_snapshot'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )

    id = models.BigIntegerField(primary_key=True)
    effective_time = models.DateField()
    active = models.BooleanField()
    module_id = models.BigIntegerField()
    module_name = models.TextField()
    definition_status_id = models.BigIntegerField()
    definition_status_name = models.TextField()
    is_primitive = models.BooleanField()
    fully_specified_name = models.TextField()
    preferred_term = models.TextField()
    definition = JSONField()
    descriptions = JSONField()
    descriptions_tsvector = SearchVectorField(null=True)
    parents = JSONField(null=True)
    children = JSONField(null=True)
    ancestors = JSONField(null=True)
    ancestor_ids = ArrayField(models.BigIntegerField(), null=True)
    descendants = JSONField(null=True)
    incoming_relationships = JSONField()
    outgoing_relationships = JSONField()
    reference_set_memberships = JSONField()

    objects = SearchManager()

    def __str__(self):
        return '{} | {} |'.format(self.preferred_term, self.id)


class Description(models.Model):
    class Meta:
        db_table = 'denormalized_description_for_current_snapshot'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )

    id = models.BigIntegerField(primary_key=True)
    effective_time = models.DateField()
    active = models.BooleanField()
    module_id = models.BigIntegerField()
    module_name = models.TextField()
    language_code = models.TextField()
    type_id = models.BigIntegerField()
    type_name = models.TextField()
    term = models.TextField()
    case_significance_id = models.BigIntegerField()
    case_significance_name = models.TextField()
    concept_id = models.BigIntegerField()
    reference_set_memberships = JSONField()


class Relationship(models.Model):
    class Meta:
        db_table = 'denormalized_relationship_for_current_snapshot'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )

    id = models.BigIntegerField(primary_key=True)
    effective_time = models.DateField()
    active = models.BooleanField()
    module_id = models.BigIntegerField()
    module_name = models.TextField()
    relationship_group = models.IntegerField()
    source_id = models.BigIntegerField()
    source_name = models.TextField()
    destination_id = models.BigIntegerField()
    destination_name = models.TextField()
    type_id = models.BigIntegerField()
    type_name = models.TextField()
    characteristic_type_id = models.BigIntegerField()
    characteristic_type_name = models.TextField()
    modifier_id = models.BigIntegerField()
    modifier_name = models.TextField()


class TransitiveClosure(models.Model):
    class Meta:
        db_table = 'transitive_closure_for_current_snapshot'

    active = models.BooleanField()
    effective_time = models.DateField()
    supertype_id = models.BigIntegerField()
    subtype_id = models.BigIntegerField()


class SimpleReferenceSetDenormalizedView(models.Model):
    """Simple value sets - no additional fields over base refset type"""
    id = models.UUIDField(editable=False, primary_key=True)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    refset_id = models.BigIntegerField(editable=False)
    refset_name = models.TextField(editable=False)

    referenced_component_id = models.BigIntegerField(editable=False)
    referenced_component_name = models.TextField(
        editable=False, null=True, blank=True)

    class Meta:
        db_table = 'simple_reference_set_expanded_view'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )


class OrderedReferenceSetDenormalizedView(models.Model):
    """Used to group components"""
    id = models.UUIDField(editable=False, primary_key=True)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    refset_id = models.BigIntegerField(editable=False)
    refset_name = models.TextField(editable=False)

    referenced_component_id = models.BigIntegerField(editable=False)
    referenced_component_name = models.TextField(
        editable=False, null=True, blank=True)

    order = models.PositiveSmallIntegerField(editable=False)

    linked_to_id = models.BigIntegerField(editable=False)
    linked_to_name = models.TextField(editable=False, null=True, blank=True)

    class Meta:
        db_table = 'ordered_reference_set_expanded_view'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )


class AttributeValueReferenceSetDenormalizedView(models.Model):
    """Used to tag components with values"""

    id = models.UUIDField(editable=False, primary_key=True)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    refset_id = models.BigIntegerField(editable=False)
    refset_name = models.TextField(editable=False)

    referenced_component_id = models.BigIntegerField(editable=False)
    referenced_component_name = models.TextField(
        editable=False, null=True, blank=True)

    value_id = models.BigIntegerField(editable=False)
    value_name = models.TextField(editable=False, null=True, blank=True)

    class Meta:
        db_table = 'attribute_value_reference_set_expanded_view'
        verbose_name = 'attrib_value_refset_view'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )


class SimpleMapReferenceSetDenormalizedView(models.Model):
    """Used for one to one maps between SNOMED and other code systems"""
    id = models.UUIDField(editable=False, primary_key=True)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    refset_id = models.BigIntegerField(editable=False)
    refset_name = models.TextField(editable=False)

    referenced_component_id = models.BigIntegerField(editable=False)
    referenced_component_name = models.TextField(
        editable=False, null=True, blank=True)

    map_target = models.CharField(max_length=256, editable=False)

    class Meta:
        db_table = 'simple_map_reference_set_expanded_view'
        verbose_name = 'simple_map_refset_view'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )


class ComplexMapReferenceSetDenormalizedView(models.Model):
    """Represent complex mappings; no additional fields"""
    id = models.UUIDField(editable=False, primary_key=True)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    refset_id = models.BigIntegerField(editable=False)
    refset_name = models.TextField(editable=False)

    referenced_component_id = models.BigIntegerField(editable=False)
    referenced_component_name = models.TextField(
        editable=False, null=True, blank=True)

    map_group = models.IntegerField(editable=False)
    map_priority = models.IntegerField(editable=False)
    map_rule = models.TextField(editable=False)
    map_advice = models.TextField(editable=False)
    map_target = models.CharField(max_length=256, editable=False)

    correlation_id = models.BigIntegerField(editable=False)
    correlation_name = models.TextField(editable=False, null=True, blank=True)

    # Optional, used only by the UK OPCS and ICD mapping fields
    map_block = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'complex_map_reference_set_expanded_view'
        verbose_name = 'complex_map_refset_view'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )


class ExtendedMapReferenceSetDenormalizedView(models.Model):
    """Like complex map refsets, but with one additional field"""
    id = models.UUIDField(editable=False, primary_key=True)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    refset_id = models.BigIntegerField(editable=False)
    refset_name = models.TextField(editable=False)

    referenced_component_id = models.BigIntegerField(editable=False)
    referenced_component_name = models.TextField(
        editable=False, null=True, blank=True)

    map_group = models.IntegerField(editable=False)
    map_priority = models.IntegerField(editable=False)
    map_rule = models.TextField(editable=False)
    map_advice = models.TextField(editable=False)
    map_target = models.CharField(max_length=256, editable=False)

    correlation_id = models.BigIntegerField(editable=False)
    correlation_name = models.TextField(editable=False, null=True, blank=True)

    map_category_id = models.BigIntegerField()
    map_category_name = models.TextField(editable=False, null=True, blank=True)

    class Meta:
        db_table = 'extended_map_reference_set_expanded_view'
        verbose_name = 'extended_map_refset_view'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )


class LanguageReferenceSetDenormalizedView(models.Model):
    """Supports creating of sets of descriptions for a language or dialect"""
    id = models.UUIDField(editable=False, primary_key=True)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    refset_id = models.BigIntegerField(editable=False)
    refset_name = models.TextField(editable=False)

    referenced_component_id = models.BigIntegerField(editable=False)
    referenced_component_name = models.TextField(
        editable=False, null=True, blank=True)

    acceptability_id = models.BigIntegerField()
    acceptability_name = models.TextField(
        editable=False, null=True, blank=True)

    class Meta:
        db_table = 'language_reference_set_expanded_view'
        verbose_name = 'lang_refset_view'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )


class QuerySpecificationReferenceSetDenormalizedView(models.Model):
    """Queries that would be run against SNOMED to generate another refset"""
    id = models.UUIDField(editable=False, primary_key=True)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    refset_id = models.BigIntegerField(editable=False)
    refset_name = models.TextField(editable=False)

    referenced_component_id = models.BigIntegerField(editable=False)
    referenced_component_name = models.TextField(
        editable=False, null=True, blank=True)

    query = models.TextField()

    class Meta:
        db_table = 'query_specification_reference_set_expanded_view'
        verbose_name = 'query_spec_refset_view'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )


class AnnotationReferenceSetDenormalizedView(models.Model):
    """Allow strings to be associated with a component - for any purpose"""
    id = models.UUIDField(editable=False, primary_key=True)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    refset_id = models.BigIntegerField(editable=False)
    refset_name = models.TextField(editable=False)

    referenced_component_id = models.BigIntegerField(editable=False)
    referenced_component_name = models.TextField(
        editable=False, null=True, blank=True)

    annotation = models.TextField()

    class Meta:
        db_table = 'annotation_reference_set_expanded_view'
        verbose_name = 'annotation_refset_view'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )


class AssociationReferenceSetDenormalizedView(models.Model):
    """Create associations between components e.g historical associations"""
    id = models.UUIDField(editable=False, primary_key=True)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    refset_id = models.BigIntegerField(editable=False)
    refset_name = models.TextField(editable=False)

    referenced_component_id = models.BigIntegerField(editable=False)
    referenced_component_name = models.TextField(
        editable=False, null=True, blank=True)

    target_component_id = models.BigIntegerField()
    target_component_name = models.TextField(
        editable=False, null=True, blank=True)

    class Meta:
        db_table = 'association_reference_set_expanded_view'
        verbose_name = 'association_refset_view'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )


class ModuleDependencyReferenceSetDenormalizedView(models.Model):
    """Specify dependencies between modules"""
    id = models.UUIDField(editable=False, primary_key=True)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    refset_id = models.BigIntegerField(editable=False)
    refset_name = models.TextField(editable=False)

    referenced_component_id = models.BigIntegerField(editable=False)
    referenced_component_name = models.TextField(
        editable=False, null=True, blank=True)

    source_effective_time = models.DateField()
    target_effective_time = models.DateField()

    class Meta:
        db_table = 'module_dependency_reference_set_expanded_view'
        verbose_name = 'module_dep_refset_view'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )


class DescriptionFormatReferenceSetDenormalizedView(models.Model):
    """Provide format and length information for different description types"""
    id = models.UUIDField(editable=False, primary_key=True)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    refset_id = models.BigIntegerField(editable=False)
    refset_name = models.TextField(editable=False)

    referenced_component_id = models.BigIntegerField(editable=False)
    referenced_component_name = models.TextField(
        editable=False, null=True, blank=True)

    description_format_id = models.BigIntegerField()
    description_format_name = models.TextField(
        editable=False, null=True, blank=True)
    description_length = models.IntegerField()

    class Meta:
        db_table = 'description_format_reference_set_expanded_view'
        verbose_name = 'desc_format_refset_view'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )


class ReferenceSetDescriptorReferenceSetDenormalizedView(models.Model):
    """Provide validation information for reference sets"""
    id = models.UUIDField(editable=False, primary_key=True)
    effective_time = models.DateField(editable=False)
    active = models.BooleanField(editable=False, default=True)

    module_id = models.BigIntegerField(editable=False)
    module_name = models.TextField(editable=False)

    refset_id = models.BigIntegerField(editable=False)
    refset_name = models.TextField(editable=False)

    referenced_component_id = models.BigIntegerField(editable=False)
    referenced_component_name = models.TextField(
        editable=False, null=True, blank=True)

    attribute_description_id = models.BigIntegerField()
    attribute_description_name = models.TextField(
        editable=False, null=True, blank=True)

    attribute_type_id = models.BigIntegerField()
    attribute_type_name = models.TextField(
        editable=False, null=True, blank=True)

    attribute_order = models.IntegerField()

    class Meta:
        db_table = 'reference_set_descriptor_reference_set_expanded_view'
        verbose_name = 'refset_descriptor_refset_view'
        unique_together = (
            'id',
            'effective_time',
            'active',
            'module_id',
        )
