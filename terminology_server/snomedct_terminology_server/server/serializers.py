from itertools import chain, groupby
from rest_framework import serializers
from .utils import get_language_name
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from django.http.request import HttpRequest

from snomedct_terminology_server.server.models import (
    Concept,
    Description,
    Relationship,
    TransitiveClosure,
    SimpleReferenceSetDenormalizedView,
    OrderedReferenceSetDenormalizedView,
    AttributeValueReferenceSetDenormalizedView,
    SimpleMapReferenceSetDenormalizedView,
    LanguageReferenceSetDenormalizedView,
    ComplexMapReferenceSetDenormalizedView,
    ExtendedMapReferenceSetDenormalizedView,
    QuerySpecificationReferenceSetDenormalizedView,
    AnnotationReferenceSetDenormalizedView,
    AssociationReferenceSetDenormalizedView,
    ModuleDependencyReferenceSetDenormalizedView,
    DescriptionFormatReferenceSetDenormalizedView,
    ReferenceSetDescriptorReferenceSetDenormalizedView
)

REFSET_MODELS = {
    'ASSOCIATION': AssociationReferenceSetDenormalizedView,
    'ATTRIBUTE_VALUE': AttributeValueReferenceSetDenormalizedView,
    'COMPLEX_MAP': ComplexMapReferenceSetDenormalizedView,
    'SIMPLE': SimpleReferenceSetDenormalizedView,
    'ORDERED': OrderedReferenceSetDenormalizedView,
    'LANGUAGE': LanguageReferenceSetDenormalizedView,
    'SIMPLE_MAP': SimpleMapReferenceSetDenormalizedView,
    'QUERY_SPECIFICATION': QuerySpecificationReferenceSetDenormalizedView,
    'MODULE_DEPENDENCY': ModuleDependencyReferenceSetDenormalizedView,
    'REFERENCE_SET_DESCRIPTOR': ReferenceSetDescriptorReferenceSetDenormalizedView,
    'EXTENDED_MAP': ExtendedMapReferenceSetDenormalizedView,
    'ANNOTATION': AnnotationReferenceSetDenormalizedView,
    'DESCRIPTION_FORMAT': DescriptionFormatReferenceSetDenormalizedView
}


def serialized_refset(refset_model):
    """Returns the serializer class for a reference set model object.
    From sil-resource, h/t @kmwenja
    """
    name = refset_model.__name__.replace('DenormalizedView', '')

    serializer_name = name + "Serializer"
    serializer_attrs = {}
    meta_attrs = {'model': refset_model}

    serializer_attrs['Meta'] = type('Meta', (object, ), meta_attrs)
    serializer_cls = type(
        serializer_name,
        (StripFieldsMixin,
         serializers.ModelSerializer,),
        serializer_attrs)
    return serializer_cls


class StripFieldsMixin(object):
    """
    Mixin to strip fields using the ?fields=<> query param.
    If used, you don't have to exclude the fields in the serializer,
    the serializer will do that for you.
    """

    effective_time = serializers.DateField(format='iso-8601')

    def __init__(self, *args, **kwargs):
        super(StripFieldsMixin, self).__init__(*args, **kwargs)
        context = getattr(self, 'context', {})
        request = context.get('request', None)

        if request:  # pragma: no branch
            to_strip = self.get_extra_strip_fields()

            exclude_fields = []

            exclude_fields += to_strip
            for i in exclude_fields:
                if i in self.fields:
                    self.fields.pop(i, None)

    def update_serializer_attribute(
            self,
            component,
            data,
            refset_models_dict):
        """Gets the full refsets that the concept/description is a member of,
        and replaces the shortened representation. This is destructive
        since it modifies the 'data' param. Use the request object from
        self.context to pass to the serialized_refset function, modified
        to remove original params.

        TODO: find a better way to get the serialized refset, that
        doesn't need a mutable request.query_params object.
        """
        refset_request = Request(HttpRequest())

        memberships_list = component.reference_set_memberships

        expanded_refsets = list(chain.from_iterable(
            [refset_models_dict[refset_membership['refset_type']].objects.filter(
                referenced_component_id=component.id,
                refset_id=refset_membership['refset_id']
            ) for refset_membership in memberships_list]
        ))

        serialized_refset_memberships = [
            serialized_refset(refset.__class__)(refset,
                                                context={'request': refset_request}).data
            for refset in expanded_refsets
        ]
        data.update({'reference_set_memberships': serialized_refset_memberships})
        return data

    def to_representation(self, obj):
        data = super(StripFieldsMixin, self).to_representation(obj)
        context = getattr(self, 'context', {})
        request = context.get('request', None)
        path = request.path
        fields = request.query_params.get('fields', None)

        show_full_model = (
            request.query_params.get(
                "full",
                "false").lower() == "true"
        )

        fields_param_not_set = fields is None or fields is ''

        if fields_param_not_set and not show_full_model:
            return data

        serialize_reference_sets = show_full_model or 'reference_set_memberships' in fields

        if serialize_reference_sets and '/terminology/refset/' not in path:
            data = self.update_serializer_attribute(
                obj,
                data,
                REFSET_MODELS
            )

        if not fields_param_not_set:
            fields = fields.split(',')

            # Obtain a sorted nested list, which is the result of
            # splitting each param field of the form
            # 'model_field.json_object_field' e.g. 'descriptions.term'
            # at the '.' character, to capture the 'term' field in each
            # json object in the 'descriptions' model field for a
            # Concept.  Sort it so that we can get all fields of the
            # 'descriptions' object together, following each other
            # alphabetically. We need this strict sorting order for
            # itertools.groupby to work properly, as it requires a
            # sorted list.

            # From the query param
            # ?fields=descriptions.term,descriptions.id,outgoing_relationships.destination_name

            # we get a list of the form
            # [['descriptions', 'id'],
            #  ['descriptions', 'term'],
            #  ['outgoing_relationships', 'destination_name']]
            # The dot '.' in a query param will begin this process, so
            # in a way I've introduced some syntax in query params.
            nested_fields_list = sorted([s.split('.')
                                         for s in fields
                                         if len(s.split('.')) == 2],
                                        key=lambda x: x[0])
            sorted_nested_fields_list = sorted(nested_fields_list, key=lambda x: x)

            # Group elements in a list of the form
            # [['descriptions', 'id'],
            #  ['descriptions', 'term'],
            #  ['outgoing_relationships', 'destination_name']]

            # Note the sorting order obtained by the previous line of
            # code.  By using the first element of each sublist, we will
            # be left with a new list of two tuples, the first element
            # of each tuple being 'descriptions' and
            # 'outgoing_relationships'. It makes it easy to loop through
            # each list without extra caching steps that add more
            # complexity.

            for field, group in groupby(sorted_nested_fields_list, key=lambda x: x[0]):
                # Resolve the captured group (which is an
                # itertools.grouper iterobject) otherwise it'll be
                # erased in subsequent iterations of line #202-#206 below.
                group = list(group)

                # The 'reference_set_memberships' field is special since
                # its full results are updated on the fly only if the
                # field is specifically requested, or if the query param
                # 'full' is true. The data object always has it if that
                # is the case. Otherwise, get the field from the model
                # object.
                if field == 'reference_set_memberships':
                    json_array = data[field]
                else:
                    try:
                        json_array = getattr(obj, field)
                    except AttributeError as e:
                        raise APIException(detail=e)

                    try:
                        assert type(json_array) == list
                    except AssertionError:
                        raise APIException(detail="""The field '{}' is not a list, but a {}. \
The '.' syntax is only valid for fields that are JSON arrays.""".format(field, type(json_array)))

                try:
                    updated_values = []
                    if len(json_array) > 0:  # pragma: no branch
                        for json_object in json_array:
                            row = {}
                            for selected_fields in group:
                                row.update(
                                    {selected_fields[1]: json_object[selected_fields[1]]}
                                )
                                updated_values.append(row)

                            # Certain values are repeated.
                            unique_values = [dict(tup)
                                             for tup in set([tuple(d.items())
                                                             for d in updated_values])]
                        data.update({field: unique_values})
                except KeyError as e:
                    raise APIException(
                        detail="""You used the key {} which is unavailable in any\
 object in the '{}' JSON array""".format(e, field))

        return data

    def get_extra_strip_fields(self):
        """
        Fetch a subset of fields from the serializer determined by the
        request's ``fields`` query parameter.
        If a request has a ``exclude_fields=true`` query parameter, the
        the fields specified are excluded.

        For example, if a resource has the fields (id, name, age, location)

        Request
            /terminology/concepts?fields=id,preferred_term

        Response

            {
                "id": "<value>",
                "preferred_term": "<value>"
            }

        Request
        /terminology/concepts?fields=id,preferred_term&exclude_fields=true

        Response

            {
                "effective_time": "<value>",
                "active": "<value>",
                 ...
            }

        This is an initial implementation that does not handle:
          - nested relationships
          - rejection of unknown fields (currently ignoring unknown fields)
          - wildcards
          - e.t.c

        Partly borrowed from @mwathi's sil_shared implementation
        see: https://github.com/savannahinformatics/sil-utilities/blob/master/sil_shared/sil_shared/serializers/mixins.py#L5  # noqa
        """
        context = getattr(self, 'context', {})
        request = context.get('request', None)
        fields = request.query_params.get('fields', None)
        exclude_fields = (
            request.query_params.get("exclude_fields", "f").lower() == "true"
        )
        show_full_model = (
            request.query_params.get(
                "full",
                "false").lower() == "true"
        )

        fields_param_not_set = fields is None or fields is ''

        if fields_param_not_set and not show_full_model:
            return ['parents',
                    'children',
                    'ancestors',
                    'descendants',
                    'reference_set_memberships',
                    'descriptions',
                    'incoming_relationships',
                    'outgoing_relationships',
                    'rank']

        elif fields_param_not_set and show_full_model:
            return []

        fields = fields.split(",")

        allowed = set(fields)
        existing = set(self.fields.keys())
        return allowed if exclude_fields else list(existing - allowed)


class ConceptListSerializer(StripFieldsMixin, serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()

    url = serializers.HyperlinkedIdentityField(
        view_name='terminology:get-concept',
        lookup_field='id'
    )

    class Meta:
        model = Concept
        fields = ('__all__')

    def get_rank(self, obj):
        request = self.context.get('request', None)
        params = request.query_params
        if params.get('search', None):
            return obj.rank
        else:
            return None


class ConceptDetailSerializer(StripFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Concept
        fields = ('__all__')


class DescriptionDetailSerializer(StripFieldsMixin, serializers.ModelSerializer):
    def to_representation(self, obj):
        data = super(DescriptionDetailSerializer, self).to_representation(obj)
        if 'language_code' in data.keys():
            data['language_name'] = get_language_name(data['language_code'])
        return data

    class Meta:
        model = Description


class DescriptionListSerializer(StripFieldsMixin, serializers.ModelSerializer):
    def to_representation(self, obj):
        data = super(DescriptionListSerializer, self).to_representation(obj)
        if 'language_code' in data.keys():
            data['language_name'] = get_language_name(data['language_code'])
        return data

    url = serializers.HyperlinkedIdentityField(
        view_name='terminology:get-description',
        lookup_field='id'
    )

    class Meta:
        model = Description
        fields = ('__all__')


class RelationshipSerializer(StripFieldsMixin, serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='terminology:get-relationship',
        lookup_field='id'
    )

    class Meta:
        model = Relationship
        fields = ('__all__')


class TransitiveClosureSerializer(StripFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = TransitiveClosure
        exclude = ('id',)
