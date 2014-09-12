import logging

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.decorators import detail_route, list_route

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from core.models import (
    ConceptDenormalizedView,
    DescriptionDenormalizedView,
    RelationshipDenormalizedView
)
from refset.models import (
    SimpleReferenceSetDenormalizedView,
    SimpleReferenceSetFull,
    OrderedReferenceSetDenormalizedView,
    OrderedReferenceSetFull,
    AttributeValueReferenceSetDenormalizedView,
    AttributeValueReferenceSetFull,
    SimpleMapReferenceSetDenormalizedView,
    SimpleMapReferenceSetFull,
    ComplexMapReferenceSetDenormalizedView,
    ComplexMapReferenceSetFull,
    ExtendedMapReferenceSetDenormalizedView,
    ExtendedMapReferenceSetFull,
    LanguageReferenceSetDenormalizedView,
    LanguageReferenceSetFull,
    QuerySpecificationReferenceSetDenormalizedView,
    QuerySpecificationReferenceSetFull,
    AnnotationReferenceSetDenormalizedView,
    AnnotationReferenceSetFull,
    AssociationReferenceSetDenormalizedView,
    AssociationReferenceSetFull,
    ModuleDependencyReferenceSetDenormalizedView,
    ModuleDependencyReferenceSetFull,
    DescriptionFormatReferenceSetDenormalizedView,
    DescriptionFormatReferenceSetFull,
    ReferenceSetDescriptorReferenceSetDenormalizedView,
    ReferenceSetDescriptorReferenceSetFull
)
from .serializers import (
    ConceptReadShortenedSerializer,
    ConceptReadFullSerializer,
    ConceptSubsumptionSerializer,
    ConceptPaginationSerializer,
    DescriptionReadSerializer,
    DescriptionPaginationSerializer,
    RelationshipReadSerializer,
    RelationshipPaginationSerializer,
    SimpleReferenceSetReadSerializer,
    SimpleReferenceSetPaginationSerializer,
    SimpleReferenceSetWriteSerializer,
    OrderedReferenceSetReadSerializer,
    OrderedReferenceSetPaginationSerializer,
    OrderedReferenceSetWriteSerializer,
    AttributeValueReferenceSetReadSerializer,
    AttributeValueReferenceSetPaginationSerializer,
    AttributeValueReferenceSetWriteSerializer,
    SimpleMapReferenceSetReadSerializer,
    SimpleMapReferenceSetPaginationSerializer,
    SimpleMapReferenceSetWriteSerializer,
    ComplexMapReferenceSetReadSerializer,
    ComplexMapReferenceSetPaginationSerializer,
    ComplexMapReferenceSetWriteSerializer,
    ExtendedMapReferenceSetReadSerializer,
    ExtendedMapReferenceSetPaginationSerializer,
    ExtendedMapReferenceSetWriteSerializer,
    LanguageReferenceSetReadSerializer,
    LanguageReferenceSetPaginationSerializer,
    LanguageReferenceSetWriteSerializer,
    QuerySpecificationReferenceSetReadSerializer,
    QuerySpecificationReferenceSetPaginationSerializer,
    QuerySpecificationReferenceSetWriteSerializer,
    AnnotationReferenceSetReadSerializer,
    AnnotationReferenceSetPaginationSerializer,
    AnnotationReferenceSetWriteSerializer,
    AssociationReferenceSetReadSerializer,
    AssociationReferenceSetPaginationSerializer,
    AssociationReferenceSetWriteSerializer,
    ModuleDependencyReferenceSetReadSerializer,
    ModuleDependencyReferenceSetPaginationSerializer,
    ModuleDependencyReferenceSetWriteSerializer,
    DescriptionFormatReferenceSetReadSerializer,
    DescriptionFormatReferenceSetPaginationSerializer,
    DescriptionFormatReferenceSetWriteSerializer,
    ReferenceSetDescriptorReadSerializer,
    ReferenceSetDescriptorPaginationSerializer,
    ReferenceSetDescriptorWriteSerializer
)

LOGGER = logging.getLogger(__name__)


class TerminologyAPIException(APIException):
    """Communicate errors that arise from wrong params to terminology APIs"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Wrong request format'


def _get_refset_ids(refset_parent_id):
    """Return all the SCTIDs that can identify a specific type of refset"""
    try:
        is_a_children = ConceptDenormalizedView.objects.get(
            concept_id=refset_parent_id
        ).is_a_children_ids
        # The return list should include the refset parent id too
        return [refset_parent_id] + list(is_a_children)
    except ConceptDenormalizedView.DoesNotExist:
        raise TerminologyAPIException(
            'No concept found for concept_id %s' % refset_parent_id)

# The many maps below are there because we are using the same (fairly compact)
# view of the different reference set types
REFSET_PARENT_IDS = {
    'simple': 446609009,
    'ordered': 447258008,
    'attribute_value': 900000000000480006,
    'simple_map': 900000000000496009,
    'complex_map': 447250001,
    'extended_map': 609331003,
    'language': 900000000000506000,
    'query_specification': 900000000000512005,
    'annotation': 900000000000516008,
    'association': 900000000000521006,
    'module_dependency': 900000000000534007,
    'description_format': 900000000000538005,
    'reference_set_descriptor': 900000000000456007
}
REFSET_READ_MODELS = {
    'simple': SimpleReferenceSetDenormalizedView,
    'ordered': OrderedReferenceSetDenormalizedView,
    'attribute_value': AttributeValueReferenceSetDenormalizedView,
    'simple_map': SimpleMapReferenceSetDenormalizedView,
    'complex_map': ComplexMapReferenceSetDenormalizedView,
    'extended_map': ExtendedMapReferenceSetDenormalizedView,
    'language': LanguageReferenceSetDenormalizedView,
    'query_specification': QuerySpecificationReferenceSetDenormalizedView,
    'annotation': AnnotationReferenceSetDenormalizedView,
    'association': AssociationReferenceSetDenormalizedView,
    'module_dependency': ModuleDependencyReferenceSetDenormalizedView,
    'description_format': DescriptionFormatReferenceSetDenormalizedView,
    'reference_set_descriptor':
    ReferenceSetDescriptorReferenceSetDenormalizedView
}
REFSET_WRITE_MODELS = {
    'simple': SimpleReferenceSetFull,
    'ordered': OrderedReferenceSetFull,
    'attribute_value': AttributeValueReferenceSetFull,
    'simple_map': SimpleMapReferenceSetFull,
    'complex_map': ComplexMapReferenceSetFull,
    'extended_map': ExtendedMapReferenceSetFull,
    'language': LanguageReferenceSetFull,
    'query_specification': QuerySpecificationReferenceSetFull,
    'annotation': AnnotationReferenceSetFull,
    'association': AssociationReferenceSetFull,
    'module_dependency': ModuleDependencyReferenceSetFull,
    'description_format': DescriptionFormatReferenceSetFull,
    'reference_set_descriptor': ReferenceSetDescriptorReferenceSetFull
}
KNOWN_REFERENCE_SET_IDS = {
    'simple': _get_refset_ids(
        REFSET_PARENT_IDS['simple']
    ),
    'ordered': _get_refset_ids(
        REFSET_PARENT_IDS['ordered']
    ),
    'attribute_value': _get_refset_ids(
        REFSET_PARENT_IDS['attribute_value']
    ),
    'simple_map': _get_refset_ids(
        REFSET_PARENT_IDS['simple_map']
    ),
    'complex_map': _get_refset_ids(
        REFSET_PARENT_IDS['complex_map']
    ),
    'extended_map': _get_refset_ids(
        REFSET_PARENT_IDS['extended_map']
    ),
    'language': _get_refset_ids(
        REFSET_PARENT_IDS['language']
    ),
    'query_specification': _get_refset_ids(
        REFSET_PARENT_IDS['query_specification']
    ),
    'annotation': _get_refset_ids(
        REFSET_PARENT_IDS['annotation']
    ),
    'association': _get_refset_ids(
        REFSET_PARENT_IDS['association']
    ),
    'module_dependency': _get_refset_ids(
        REFSET_PARENT_IDS['module_dependency']
    ),
    'description_format': _get_refset_ids(
        REFSET_PARENT_IDS['description_format']
    ),
    'reference_set_descriptor': _get_refset_ids(
        REFSET_PARENT_IDS['reference_set_descriptor']
    )
}
REFSET_READ_DETAIL_SERIALIZERS = {
    'simple': SimpleReferenceSetReadSerializer,
    'ordered': OrderedReferenceSetReadSerializer,
    'attribute_value': AttributeValueReferenceSetReadSerializer,
    'simple_map': SimpleMapReferenceSetReadSerializer,
    'complex_map': ComplexMapReferenceSetReadSerializer,
    'extended_map': ExtendedMapReferenceSetReadSerializer,
    'language': LanguageReferenceSetReadSerializer,
    'query_specification': QuerySpecificationReferenceSetReadSerializer,
    'annotation': AnnotationReferenceSetReadSerializer,
    'association': AssociationReferenceSetReadSerializer,
    'module_dependency': ModuleDependencyReferenceSetReadSerializer,
    'description_format': DescriptionFormatReferenceSetReadSerializer,
    'reference_set_descriptor': ReferenceSetDescriptorReadSerializer
}
REFSET_READ_PAGINATED_LIST_SERIALIZERS = {
    'simple': SimpleReferenceSetPaginationSerializer,
    'ordered': OrderedReferenceSetPaginationSerializer,
    'attribute_value': AttributeValueReferenceSetPaginationSerializer,
    'simple_map': SimpleMapReferenceSetPaginationSerializer,
    'complex_map': ComplexMapReferenceSetPaginationSerializer,
    'extended_map': ExtendedMapReferenceSetPaginationSerializer,
    'language': LanguageReferenceSetPaginationSerializer,
    'query_specification':
    QuerySpecificationReferenceSetPaginationSerializer,
    'annotation': AnnotationReferenceSetPaginationSerializer,
    'association': AssociationReferenceSetPaginationSerializer,
    'module_dependency': ModuleDependencyReferenceSetPaginationSerializer,
    'description_format':
    DescriptionFormatReferenceSetPaginationSerializer,
    'reference_set_descriptor': ReferenceSetDescriptorPaginationSerializer
}
REFSET_WRITE_SERIALIZERS = {
    'simple': SimpleReferenceSetWriteSerializer,
    'ordered': OrderedReferenceSetWriteSerializer,
    'attribute_value': AttributeValueReferenceSetWriteSerializer,
    'simple_map': SimpleMapReferenceSetWriteSerializer,
    'complex_map': ComplexMapReferenceSetWriteSerializer,
    'extended_map': ExtendedMapReferenceSetWriteSerializer,
    'language': LanguageReferenceSetWriteSerializer,
    'query_specification': QuerySpecificationReferenceSetWriteSerializer,
    'annotation': AnnotationReferenceSetWriteSerializer,
    'association': AssociationReferenceSetWriteSerializer,
    'module_dependency': ModuleDependencyReferenceSetWriteSerializer,
    'description_format': DescriptionFormatReferenceSetWriteSerializer,
    'reference_set_descriptor': ReferenceSetDescriptorWriteSerializer
}


def _refset_map_lookup(refset_id, MAP, err_msg_description):
    """A helper that is used by the next five functions"""
    for refset_type, known_ids in KNOWN_REFERENCE_SET_IDS.iteritems():
        if long(refset_id)in known_ids:
            return MAP[refset_type]

    raise TerminologyAPIException(
        'Cannot find a %s for refset_id %s' % (err_msg_description, refset_id)
    )


def _get_refset_list_serializer(refset_id):
    """Given a refset_id, return the correct paginated ( list ) serializer"""
    return _refset_map_lookup(
        refset_id, REFSET_READ_PAGINATED_LIST_SERIALIZERS, 'list serializer'
    )


def _get_refset_detail_serializer(refset_id):
    """Given a refset_id, return the correct detail ( item ) serializer"""
    return _refset_map_lookup(
        refset_id, REFSET_READ_DETAIL_SERIALIZERS, 'detail serializer'
    )


def _get_refset_write_serializer(refset_id):
    """Given a refset_id, return the correct write serializer"""
    return _refset_map_lookup(
        refset_id, REFSET_WRITE_SERIALIZERS, 'write serializer'
    )


def _get_refset_read_model(refset_id):
    """Given a refset_id, return the correct denormalized view"""
    return _refset_map_lookup(
        refset_id, REFSET_READ_MODELS, 'denormalized view model'
    )


def _get_refset_write_model(refset_id):
    """Given a refset_id, return the correct model for writes"""
    return _refset_map_lookup(
        refset_id, REFSET_WRITE_MODELS, 'write model'
    )


def _paginate_queryset(request, queryset):
    """A helper that abstracts away the details of paginating a queryset"""
    paginator = Paginator(queryset, settings.REST_FRAMEWORK['PAGINATE_BY'])
    page = request.QUERY_PARAMS.get('page')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
    return results


def _check_if_module_id_belongs_to_namespace(module_id, namespace_id=None):
    """A helper that is used in validation

    :param module_id:
    :param namespace_id: if not supplied, the default namespace is used
    """
    # Use the default namespace if one is not supplied
    if not namespace_id:
        namespace_id = settings.SNOMED_NAMESPACE_IDENTIFIER
    if str(namespace_id) not in str(module_id):
        raise TerminologyAPIException(
            'Module %s is not in namespace %s' % (module_id, namespace_id))


class ConceptView(viewsets.ViewSet):
    """**View concepts with their metadata, relationships and descriptions**

    # Retrieval Services
    This service should be called with a URL of the form
    `/terminology/concepts/<concept_id>/<representation_type>/`.

    The `representation_type` parameter determines whether a full /
    detailed representation ( resource heavy ) or a lightweight representation
    ( resource light ) is sent. The valid choices for this parameter are:

     * `shortened` - the default, render a bandwidth and CPU/memory saving
     representation; **include only direct parents / children**
     * `full` - render the full denormalized representation

    **`representation_type` is optional** - if not sent, the default of
    `shortened` will be applied.

    The following **shortcut** URLs are defined:

     * `/terminology/concepts/root/<representation_type>/` - information
     pertaining to the root concept
     * `/terminology/concepts/is_a/<representation_type>/` - information
     pertaining to the |is a| relationship type. This is the most important
     type of relationship
     * `/terminology/concepts/core_metadata/<representation_type>/` -
     information pertaining to core **metadata** concepts. Core metadata
     concepts are those that are referenced from fields within core SNOMED
     components ( concepts, descriptions, relationships, identifiers )
     * `/terminology/concepts/foundation_metadata/<representation_type>/` -
     information pertaining to foundation **metadata** concepts. Foundation
     metadata concepts support the extensibility mechanism e.g definition
     of reference sets
     * `/terminology/concepts/reference_set/<representation_type>/` -
     information relating to reference sets
     * `/terminology/concepts/attribute/<representation_type>/` -
     information relating to attributes. Attributes are used to define
     concepts e.g using the |Finding Site| and |Associated Morphology|
     to define a clinical finding.
     * `/terminology/concepts/relationship_type/<representation_type>/` -
     information relating to relationship types. |is a| is one of many types
     of relationship.
     * `/terminology/concepts/namespace/<representation_type>/` -
     information relating to namespaces. New SNOMED content can only be
     created by organizations that have been assigned namespaces.
     * `/terminology/concepts/navigational/<representation_type>/` -
     information relating to navigational concepts. These are concepts that
     do not have any intrinsic information value - existing solely for the
     purpose of defining navigation hierarchies
     * `/terminology/concepts/module/<representation_type>/` - information on
     modules. Components are attached to modules, which are in turn
     associated with a namespace.
     * `/terminology/concepts/definition_status/<representation_type>/` -
     information on valid definition statuses. Concepts from this hierarchy are
     used to distinguish between fully and partially defined concepts
     * `/terminology/concepts/description_type/<representation_type>/` -
     information on available description types. Information from these
     concepts can be used for validation
     * `/terminology/concepts/case_significance/<representation_type>/` -
     concepts that can be used to define the case significance of descriptions
     * `/terminology/concepts/characteristic_type/<representation_type>/` -
     used to define whether a relationship is defining, additional or
     qualifying
     * `/terminology/concepts/modifier/<representation_type>/` -
     used to define modifiers that could be applied to a relationship e.g "All"
     or "Some"
     * `/terminology/concepts/identifier_scheme/<representation_type>/` -
     defines the type of SNOMED identier e.g integer or UUID
     * `/terminology/concepts/attribute_value/<representation_type>/` -
     defines reference set attributes

    # Creating new concepts
    ## POST format
    `POST` to `/terminology/concepts/` a JSON payload of the following form:

        {
            'effective_time': <a date, in YYYYMMDD ISO-8601 format>,
            'active': `true` of `false`,
            'module_id': <SCTID, a module in this server's namespace>,
            'definition_status_id': <SCTID>
        }

    ## Return format
    The terminology server will assign a `component_id` automatically, and
    return a representation of the newly created concept:

        {
            `component_id`: <newly assigned SCTID>,
            'effective_time': <a date, in YYYYMMDD ISO-8601 format>,
            'active': `true` of `false`,
            'module_id': <SCTID, a module in this server's namespace>,
            'definition_status_id': <SCTID>
        }

    The valid concept IDs for `definition_status_id` can be obtained by issuing
    a `GET` to `/terminology/concepts/definition_status/`.

    The valid concept IDs for `module_id` can be obtained by issuing a `GET` to
    `/terminology/admin/namespace/`. There is a bit of a "chicken-and-egg"
    problem around the creation of new modules.

    Module creation is a special case where:

     * the `module_id` should be the same as the `component_id`
     * the `module_id` should not previously exist in the database
     * the `effective_time` must not be in the past


    # Updating existing concepts
    The `PUT` format for the update of an existing concept is the same as the
    format returned after creating a new concept. The return format is the same
    too.

    `PUT` to `/terminology/concepts`.

    # Inactivating concepts
    Note - even though the HTTP verb in use is `DELETE`, you must not think of
    this as "deleting". SNOMED RF2 is modeled as a log structured archive,
    where "deleting" involves adding a new row with the `active` field set to
    `false` and a new ( more recent ) `effective_time`.

    Issue a `DELETE` to `/terminology/concepts/`.

    # Important Note
    A newly added component is **not immediately available** in the search and
    enumeration APIs. A build must be triggered - by issuing a `GET` to
    `/terminology/admin/build/`. From a workflow perspective, it is prudent to
    **treat builds as the last stage in a batch process** i.e. do not trigger a
    build after every niggling little change. This is because the build process
    will increment the `effective_time` of each component in a module if any
    other component in the module has had a change. **The build step should be
    treated as a release step.**
    """
    def retrieve(self, request, concept_id=None,
                 representation_type='shortened'):
        """
        :param request:
        :param concept_id:
        :param representation_type:
        :return:
        """
        if representation_type not in ['shortened', 'full']:
            raise TerminologyAPIException(
                'Unknown representation type: %s' % representation_type)

        concepts = ConceptDenormalizedView.objects.filter(
            concept_id=concept_id)
        serializer = ConceptReadShortenedSerializer \
            if representation_type == 'shortened' \
            else ConceptReadFullSerializer
        return Response(serializer(concepts, many=True).data)

    def list(self, request):
        """Paginated list of concepts
        :param request:
        """
        queryset = ConceptDenormalizedView.objects.all()
        serializer = ConceptPaginationSerializer(
            _paginate_queryset(request, queryset),
            context={'request': request}
        )
        return Response(serializer.data)

    def create(self, request, module_id):
        """Add a new concept - in the indicated module

        :param request:
        :param module_id: SNOMED ID of module in which the new concept will be
        created

        The `module_id` must be explicitly specified. It must also be one of
        the modules that belong to this terminology server's namespace.

        There is a bit of a chicken and egg problem - around the creation of
        the first module.
        """
        _check_if_module_id_belongs_to_namespace(module_id)
        # TODO Guarantee that there is no component_id
        # TODO Validate the POSTed payload ( by deserializing it; validators in serializers )
        # TODO Save
        # TODO Return a success message that acknowledges success and advises the user to schedule a rebuild when finished
        pass

    def update(self, request, concept_id):
        """Update an existing concept.

        :param request:
        :param concept_id:

        This should only be possible for concepts that belong to this server's
        namespace.
        """
        # TODO Check that the concept_id belongs to our modules
        # TODO Validate the PUT paload ( by deserializing it; validators in serializers )
        # TODO Save
        # TODO Make necesary changes to the module's "effectiveTime"
        # TODO Return a success message that acknowledges success and advises the user to schedule a rebuild when finished
        pass

    def destroy(self, request, concept_id):
        """**INACTIVATE** an existing concept.

        :param request:
        :param concept_id:

        This should only be possible for concepts that belong to this server's
        namespace.
        """
        # TODO Check that the concept_id belongs to our modules
        # TODO Inactivate the concept
        # TODO Make necesary changes to the module's "effectiveTime"
        # TODO Return a success message that acknowledges success and advises the user to schedule a rebuild when finished
        pass


class SubsumptionView(viewsets.ViewSet):
    """Identify a concept's parents, ancestors, children, descendants

    This service should be called with a URL of the form:

    ```
    /terminology/subsumption/<concept_id>/
    ```
    """
    def retrieve(self, request, concept_id=None):
        """
        :param request:
        :param concept_id:
        :return:
        """
        try:
            concept = ConceptDenormalizedView.objects.get(
                concept_id=concept_id)
            return Response(ConceptSubsumptionSerializer(concept).data)
        except ConceptDenormalizedView.DoesNotExist:
            raise TerminologyAPIException(
                'There is no concept with SCTID %s' % concept_id)


class RefsetView(viewsets.ViewSet):
    """Create, retrieve, update and inactivate reference set members

    This API does not facilitate the creation of new reference set types.

    The general URL form is:

    ```
    /terminology/refset/<refset_sctid>/
    ```

    The following **shortcut** URLs are defined:

    * `/terminology/refset/simple/`
    * `/terminology/refset/ordered/`
    * `/terminology/refset/attribute_value/`
    * `/terminology/refset/simple_map/`
    * `/terminology/refset/complex_map/`
    * `/terminology/refset/extended_map/`
    * `/terminology/refset/language/`
    * `/terminology/refset/query_specification/`
    * `/terminology/refset/annotation/`
    * `/terminology/refset/association/`
    * `/terminology/refset/module_dependency/`
    * `/terminology/refset/description_format/`

    Reference sets may be filtered by `module_id` as follows:

    ```
    /terminology/refset/<refset_sctid>/<module_id>/
    ```

    This filtering pattern will also work with the shortcuts defined above.
    For example:
        * `/terminology/refset/simple/<module_id>/`
        * ...the same pattern for all other shortcuts...
    """
    def retrieve(self, request, refset_id, entry_id):
        """Retrieve a single refset entry
        """
        serializer = _get_refset_detail_serializer(refset_id)
        model = _get_refset_read_model(refset_id)
        items = model.objects.filter(refset_id=refset_id, row_id=entry_id)
        return Response(serializer(items, many=True).data)

    def list(self, request, refset_id, module_id=None):
        """Paginated listing of refset conctent
        :param request:
        :param refset_id: identifies the reference set that is to be listed
        :param module_id: ( optional ) filter by the module entries belong to

        If the `module_id` is not supplied, all applicable refset content will
        be listed.
        """
        # TODO Modify base serializer so as to embed link to detail view
        # TODO referenced_component_name in language_reference_set needs to be non null
        model = _get_refset_read_model(refset_id)
        refset_ids = _get_refset_ids(refset_id)
        if module_id:
            queryset = model.objects.filter(
                refset_id__in=refset_ids, module_id=module_id)
        else:
            queryset = model.objects.filter(refset_id__in=refset_ids)
        serializer = _get_refset_list_serializer(refset_id)(
            _paginate_queryset(request, queryset),
            context={'request': request}
        )
        return Response(serializer.data)

    def create(self, request, refset_id, module_id):
        """Add a new refset member

        :param request:
        :param refset_id: identifies the reference set that is to be listed
        :param module_id: add new content to the specified module

        For this specific endpoint, the `module_id` is not optional. This is an
        intentional choice - to make the "attaching" of new content to a module
        explicit rather than implicit.
        """
        _check_if_module_id_belongs_to_namespace(module_id)
        pass

    def update(self, request, concept_id, refset_id, entry_uuid):
        """Update an existing reference set entry
        """
        pass

    def destroy(self, request, concept_id, refset_id, entry_uuid):
        """**INACTIVATE** a refset entry
        """
        pass


class DescriptionView(viewsets.ViewSet):
    def retrieve(self, request, component_id):
        """Retrieve a single description

        :param request:
        :param component_id: the description's SNOMED identifier

        This endpoint returns a list because one SNOMED identifier can have
        multiple rows ( e.g multiple versions ).
        """
        results = DescriptionDenormalizedView.objects.filter(
            component_id=component_id
        )
        return Response(DescriptionReadSerializer(results, many=True).data)

    def list(self, request):
        """Paginated listing of descriptions

        :param request:
        """
        queryset = DescriptionDenormalizedView.objects.all()
        serializer = DescriptionPaginationSerializer(
            _paginate_queryset(request, queryset),
            context={'request': request}
        )
        return Response(serializer.data)

    def create(self, request, module_id):
        _check_if_module_id_belongs_to_namespace(module_id)
        pass

    def update(self, request, concept_id):
        pass

    def destroy(self, request, concept_id):
        pass


class RelationshipView(viewsets.ViewSet):
    def retrieve(self, request, component_id):
        """Retrieve a single relationship

        :param request:
        :param component_id: the relationship's SNOMED identifier

        This endpoint returns a list because one SNOMED identifier can have
        multiple rows ( e.g multiple versions ).
        """
        relationships = RelationshipDenormalizedView.objects.filter(
            component_id=component_id
        )
        return Response(
            RelationshipReadSerializer(relationships, many=True).data
        )

    def list(self, request):
        """Paginated listing of relationships

        :param request:
        """
        queryset = RelationshipDenormalizedView.objects.all()
        serializer = RelationshipPaginationSerializer(
            _paginate_queryset(request, queryset),
            context={'request': request}
        )
        return Response(serializer.data)

    def create(self, request, module_id):
        """**ADD** a new relationship

        The new relationship must be assigned to a module that belongs to this
        server's namespace.
        """
        _check_if_module_id_belongs_to_namespace(module_id)
        pass

    def update(self, request, concept_id):
        """**MODIFY** an existing relationship

        This should only be possible for a relationship that belongs to this
        server's namespace.
        """
        pass

    def destroy(self, request, concept_id):
        """**INACTIVATE* a relationship**

        This should only be possible for content that belongs to this server's
        namespace.
        """
        pass


class AdminView(viewsets.ViewSet):
    """Perform administrative tasks and introspect the server's data

    In order to obtain a map with this server's namespace and its registered
    modules, issue a `GET` to `/terminology/admin/namespace/`.

    In order to trigger an export / backup of this server's custom content,
    issue a `GET` to `/terminology/admin/export/`.

    In order to trigger a rebuild ( refresh of all materialized views, needed
    after a content update ), issue a `GET` to `/terminology/admin/build/`.
    """
    @detail_route(methods=['get'])
    def namespace(self, request):
        # TODO return a map that has this server's namespace and its modules
        pass

    @detail_route(methods=['get'])
    def export(self, request, namespace_id=None):
        # TODO If a namespace ID is not given, export this server's namespace
        # TODO Work out a format that can be processed by the load tools
        pass

    @detail_route(methods=['get'])
    def build(self, request):
        # TODO Queue a build then return a success message
        # TODO Increment effective_time if there has been a change in any
        # component in a module
        pass

    @detail_route(methods=['get'])
    def release(self, request):
        """Information about the current release"""
        pass

    @list_route(methods=['get'])
    def releases(self, request):
        """Information about all the releases known to this server"""
        pass
