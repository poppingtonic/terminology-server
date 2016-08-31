from itertools import chain
from rest_framework import serializers
from .utils import get_language_name

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
        context = getattr(self, 'context', {})
        request = context.get('request', None)
        request.query_params._mutable = True
        request.query_params.pop('fields', None)

        if 'ReferenceSet' in component.__class__.__name__:
            return data
        else:
            memberships_list = data['reference_set_memberships']

            expanded_refsets = list(chain.from_iterable(
                [refset_models_dict[refset_membership['refset_type']].objects.filter(
                    referenced_component_id=component.id,
                    refset_id=refset_membership['refset_id']
                ) for refset_membership in memberships_list]
            ))

            serialized_refset_memberships = [
                serialized_refset(refset.__class__)(refset, context={'request': request}).data
                for refset in expanded_refsets
            ]
            data.update({'reference_set_memberships': serialized_refset_memberships})
            return data

    def to_representation(self, obj):
        data = super(StripFieldsMixin, self).to_representation(obj)
        context = getattr(self, 'context', {})
        request = context.get('request', None)

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

        if serialize_reference_sets:
            return self.update_serializer_attribute(
                obj,
                data,
                REFSET_MODELS
            )
        else:
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
                    'outgoing_relationships']

        elif fields_param_not_set and show_full_model:
            return []

        fields = fields.split(",")

        allowed = set(fields)
        existing = set(self.fields.keys())
        return allowed if exclude_fields else list(existing - allowed)


class ConceptListSerializer(StripFieldsMixin, serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='terminology:get-concept',
        lookup_field='id'
    )

    class Meta:
        model = Concept
        fields = ('__all__')


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


class DescriptionListSerializer(StripFieldsMixin, serializers.HyperlinkedModelSerializer):
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


class RelationshipSerializer(StripFieldsMixin, serializers.HyperlinkedModelSerializer):
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
