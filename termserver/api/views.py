import logging
import sys
import copy
import uuid
import traceback

from dateutil import parser
from operator import itemgetter

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.decorators import detail_route, list_route
from rest_framework.reverse import reverse

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.utils import ProgrammingError
from django.db.models import Max
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from celery import chain

from core.helpers import verhoeff_digit
from core.models import (
    ConceptFull,
    DescriptionFull,
    RelationshipFull,
    ConceptDenormalizedView,
    DescriptionDenormalizedView,
    RelationshipDenormalizedView,
    ServerNamespaceIdentifier
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
from administration.management.commands.shared.load import (
    refresh_dynamic_snapshot, refresh_materialized_views
)
from .serializers import (
    _confirm_concept_descends_from,
    ConceptReadShortenedSerializer,
    ConceptReadFullSerializer,
    ConceptSubsumptionSerializer,
    ConceptWriteSerializer,
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
RELEASE_STATUSES = {
    'R': 'Released',
    'D': 'Development',
    'E': 'Evaluation'
}
PARTITION_IDENTIFIERS = {
    'CONCEPT': 10,
    'DESCRIPTION': 11,
    'RELATIONSHIP': 12
}


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
        # This is needed because this code runs on Django initialization
        # During a build, the views will not exist and the tables will be empty
        build_commands = [
            'build', 'load_snomed', 'reset', 'reset_and_load',
            'load_full_release', 'shell', './manage.py', 'manage.py'
        ]
        is_build = False
        for build_command in build_commands:
            if build_command in sys.argv:
                is_build = True

        if not is_build:
            raise TerminologyAPIException(
                'No concept found for concept_id %s' % refset_parent_id)
    except ValidationError as ex:
        traceback.print_exc()
        raise TerminologyAPIException(
            'Validation error "%s" when loading refset ids for parent %s' %
            (ex.messages, refset_parent_id)
        )
    except ProgrammingError as e:
        LOGGER.debug('%s [OK during a build/reload process]' % e.message)

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


def _confirm_component_id_does_not_exist(component_id):
    """Validation - confirm that the `component_id` isn't yet in our database

    :param component_id:
    """
    models = (ConceptFull, DescriptionFull, RelationshipFull)
    for model in models:
        try:
            model.objects.get(component_id=component_id)
            raise TerminologyAPIException(
                'Programming Error: SCTID %s is already in use in %s' %
                (component_id, model)
            )
        except model.DoesNotExist:
            pass  # This is OK; if the component_id is not used, we proceed


def _allocate_new_component_id(component_type):
    """Allocate a new SCTID when creating a new component

    `component_type` should be one of: `CONCEPT`, `DESCRIPTION` or
    `RELATIONSHIP`.

    This function **allocated a new identifier each time it is called**. This
    means that **in cases where the component creation process fails after the
    allocation of an id, the allocated identifier will not be used; it will be
    a 'gap' in our namespace**. This approach has been chosen because it is
    predictable.

    As implemented, there is the possibility of a race condition. No effort has
    been expended in alleviating that problem - because terminology creation is
    expected to largely be a 'single stream' activity ( a sinle editor working
    on new content at any particular time ).

    The allocated SCTID check digits were verified using the form located at
    http://www.augustana.ab.ca/~mohrj/algorithms/checkdigit.html

    :param component_type:
    """
    # First, validate the component_type param
    if component_type not in PARTITION_IDENTIFIERS.keys():
        raise TerminologyAPIException(
            'Unknown component type: %s' % component_type)

    # Look up the next available extension item identifier and reserve it
    current_max = ServerNamespaceIdentifier.objects.filter(
        extension_item_type=component_type
    ).aggregate(Max('extension_item_identifier'))
    if not current_max['extension_item_identifier__max']:
        current_max['extension_item_identifier__max'] = 0
    new_item_identifier = current_max['extension_item_identifier__max'] + 1
    ServerNamespaceIdentifier.objects.create(
        extension_item_identifier=new_item_identifier,
        extension_item_type=component_type
    )
    # Generate an SCTID
    new_sctid = (
        str(new_item_identifier) +
        str(settings.SNOMED_NAMESPACE_IDENTIFIER) +
        str(PARTITION_IDENTIFIERS[component_type])
    )
    sctid_with_check = new_sctid + str(verhoeff_digit(new_sctid))
    _confirm_component_id_does_not_exist(sctid_with_check)
    return sctid_with_check


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

    There is a separate API endpoint for the creation of new modules in this
    server's namespace ( `POST` requests to `/terminology/admin/namespace/`).
    Refer to the documentation that is embedded in that endpoint.

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
        # We want fully qualified URLs; so we need a request
        # Hence the location of this code
        for item in serializer.data['results']:
            item['detail_url'] = reverse(
                'terminology:concept-detail-extended',
                kwargs={
                    'concept_id': str(item['concept_id']),
                    'representation_type': 'full'
                },
                request=request
            )
        return Response(serializer.data)

    def create(self, request, module_id):
        """Add a new concept - in the indicated module

        :param request:
        :param module_id: SNOMED ID of module in which the new concept will be
        created

        The `module_id` must be explicitly specified. It must also be one of
        the modules that belong to this terminology server's namespace.

        This API assumes that the modules already exist. There is a dedicated
        API for module creation - `POST`s to `/terminology/admin/namespace/`.

         * `component_id` is created automatically.
         * `effective_time` is *optional*. It defaults to the current date.
         * `active` is *optional*. It defaults to `True`.
         * `module_id` is sent in via the query format.
         * `definition_status_id` is the only compulsory field
        """
        # Check that the module_id is one that we can create content in
        _check_if_module_id_belongs_to_namespace(module_id)

        # Check for conformance to the format
        input_data = request.DATA.copy()
        if 'definition_status_id' not in input_data:
            raise TerminologyAPIException(
                '`definition_status_id` must be supplied')

        if 'component_id' in input_data:
            raise TerminologyAPIException(
                'The `component_id` must not be supplied; it is auto-assigned')

        # Use the serializer to clean and validate the data
        input_data['component_id'] = _allocate_new_component_id('CONCEPT')
        serializer = ConceptWriteSerializer(data=input_data)
        if serializer.is_valid():
            # TODO Mark is_new as True
            # TODO Mark is_updated as False
            serializer.save()
            return Response({
                'message': 'OK; queue a build when you finish adding content',
                'build_url': reverse('terminology:build', request=request),
                'concept_detail_url': reverse(
                    'terminology:concept-detail-extended',
                    kwargs={
                        'concept_id': input_data['component_id'],
                        'representation_type': 'full'
                    },
                    request=request
                )
            })
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def update(self, request, concept_id):
        """Update an existing concept.

        :param request:
        :param concept_id:

        This should only be possible for concepts that belong to this server's
        namespace.
        """
        try:
            serializer = ConceptWriteSerializer(data=request.DATA)
            if serializer.is_valid():
                # Retrieve the concept
                concept = serializer.data['component_id']

                # We should only edit concepts that belong to our namespace
                _check_if_module_id_belongs_to_namespace(concept.module_id)

                # Add markers that will be used to "update" the module during build
                # TODO Mark the newly updated concept as "dirty"
                ## Inactivate existing ( last record )
                ## Create a new record with the same concept_id and a new effective_time
                ## Mark is_updated as True and is_new as False for the old record
                ## Mark is_new as True and is_updated as False for the new record
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except ConceptFull.DoesNotExist:
            raise TerminologyAPIException(
                'Concept with concept_id %s not found' % concept_id
            )
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
        concepts = ConceptFull.objects.filter(
            component_id=concept_id, active=True)
        if concepts:
            # Check that the concept_id belongs to our modules
            map(_check_if_module_id_belongs_to_namespace, concepts)

            # Inactivate each record
            for concept in concepts:
                # Zero the pk, so that when we save we get a new pk
                new_copy = copy.copy(concept)
                new_copy.id = None
                new_copy.active = False
                new_copy.effective_time = timezone.now()
                new_copy.save()
                # TODO Mark as dirty - so that the module effective_time can be upgraded in the build process

            # Return a success message after deleting
            return Response({
                'message': 'Deleted; build when you finish editing content',
                'build_url': reverse('terminology:build', request=request)
            })
        else:
            raise TerminologyAPIException(
                'No concepts with component_id %s' % concept_id)


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

    This API does not facilitate the creation of new reference set **types**.

    # Retrieval
    This is accomplished by issuing a `GET` to a URL of the following form:

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
    * `/terminology/refset/reference_set_descriptor/`

    Reference sets may be filtered by `module_id` as follows:

    ```
    /terminology/refset/<refset_sctid>/<module_id>/
    ```

    This filtering pattern will also work with the shortcuts defined above.
    For example:
        * `/terminology/refset/simple/<module_id>/`
        * ...the same pattern for all other shortcuts...

    # Adding reference set content
    This involves `POST` reqyests to URLs of the following form:

    ```
    /terminology/refset/<refset_id>/<module_id>/

    Each reference set type has its own payload format.

    ## Payload formats
    ### Common fields ( common to all reference set types )
    All reference set members will share the following fields:

    ```
    {
        'id': <a UUID>, // uniquely identifies a single row or entry
        'effective_time': <a date, in YYYYMMDD ISO-8601 format>,
        'active': <boolean>,
        'referenced_component_id': <SCTID> // usually reserved for "the thing
            // that this reference set is about" e.g for a simple reference
            // set, this is the field that will contain the IDs of the values
            // that are to be enumerated
    }
    ```

    The `refset_id` ( which determines what kind of reference set it is )
    and `module_id` ( which links the refset to a module and ultimately to a
    maintaining organization ) will be extracted from the URL.

    The terminology server will enforce the rule that **content will only be
    created for `module_id`s that belong to this server's namespace**. A
    listing of the `module_id`s that are applicable can be obtained from
    <http:/terminology/admin/namespace/>.

    ### Simple reference sets
    The `refset_id` should be set to one of the descendants ( children ) of
    <http:/terminology/concepts/446609009/>.

    For the `referenced_component_id`, it is important to take a broad view of
    what a **component** is in SNOMED. Descriptions, relationships, concepts
    and identifiers are all *components* - so the SCTID of any of these would
    be a valid `referenced_component_id`. However, common sense demands that
    *a single reference set* should hold components of the same type.

    Simple reference sets do not have any additional fields.

    ### Ordered reference sets
    The `refset_id` should be set to one of the descendants ( children ) of
    <http:/terminology/concepts/447258008/>.

    The `referenced_component_id` will be a link to the component that is to be
    included in the ordered set. The same broad interpretation of what a
    "component" is that was mentioned above will apply.

    The following additional fields should be added to the JSON payload:

     * `order` - an unsigned integer, must be greater than one
     * `linked_to_id` - to link members into a sub-group, all components in the
     same sub-group shpuld reference the component in the group that has an
     order of "1"

    The terminology server will carry out the following sanity checks:
     * ensure that an `order` value is not repeated *within the same refset*
     * ensure that `order` values are integers, greater than or equal to one
     * ensure that the `linked_to_id` points to a component whose `order` is 1

    ### Attribute value reference sets
    The `refset_id` should be set to one of the descendants ( children ) of
    <http:/terminology/concepts/900000000000480006/>.

    The `referenced_component_id` will be a reference to the SNOMED *component*
    that is to be tagged with a value. As was the case above, we take a broad
    view of what a "component" is.

    The only additional field is `value_id`, which should be set to a
    descendant of <http:/terminology/concepts/900000000000491004/>.

    ### Simple map reference sets
    The `refset_id` should be set to one of the descendants ( children ) of
    <http:/terminology/concepts/900000000000496009/>.

    The `referenced_component_id` will be a reference to the SNOMED *component*
    that is to be mapped.

    The only additional field is `map_target` - a text field. This should be
    used to hold the value of the code in the alternate mapping scheme.

    ### Complex map reference sets
    The `refset_id` should be set to one of the descendants ( children ) of
    <http:/terminology/concepts/447250001/>.

    The `referenced_component_id` will be a reference to the SNOMED *component*
    that is to be mapped.

    The JSON payload should include the following additional fields:

     * `map_group` - create sets of map records; out of which one may be chosen
     during a specific mapping operation
     * `map_priority` - the order in which map records should be checked at
     runtime; first one wins
     * `map_rule` - a machine readable map rule
     * `map_advice` - human readable guidance
     * `map_target` - the target code in the scheme to be mapped
     * `correlation_id` - set to a descendant of
     <http:/terminology/concepts/447247004/>

    The terminology server will perform the following sanity checks:

     * ensure that `map_group` and `map_priority` are allocated on a sequential
     basis and are not repeated

    ### Extended map reference sets
    The `refset_id` should be set to one of the descendants ( children ) of
    <http:/terminology/concepts/609331003/>.

    All the additional fields for this type of reference set will be the same
    as those for complex map reference sets. There is one additional field:

     * `map_category_id` - set to a descendant of
     <http:/terminology/concepts/609331003/>

    ### Language reference sets
    The `refset_id` should be set to one of the descendants ( children ) of
    <http:/terminology/concepts/900000000000506000/>.

    The `referenced_component_id` should refer to a **description**, and not to
    any other kind of component.

    The `type_id` should be set to one of:

     * <http:/terminology/concepts/900000000000003001/> - fully specified name
     * <http:/terminology/concepts/900000000000013009/> - synonym

    The only additional field is `acceptability_id` - which should be set to
    one of:

     * <http:/terminology/concepts/900000000000548007/> - preferred term

    The terminology server will enforce the following sanity checks:

     * that there is at most one fully specified name ( per concept ) within
     the same language reference set
     * that there must be only one description for each concept that has a
     `type_id` corresponding to "synonym" and an `acceptability_id` that
     corresponds to "preferred"

    ### Query specification reference sets
    The `refset_id` should be set to one of the descendants ( children ) of
    <http:/terminology/concepts/900000000000512005/>.

    The `referenced_component_id` is the SCTID of the refset for which the
    members are to be generated.

    There is only one additional field:

     * `query` - string; the query that will be used to re-generate the refset
     members

    ### Annotation reference sets
    The `refset_id` should be set to one of the descendants ( children ) of
    <http:/terminology/concepts/900000000000516008/>.

    The `referenced_component_id` is the SCTID of a component that is to be
    annotated.

    There is only one additional field:

     * `annotation` - string; the annotation to attach to the component

    ### Association reference sets
    The `refset_id` should be set to one of the descendants ( children ) of
    <http:/terminology/concepts/900000000000521006/>.

    The `referenced_component_id` is a reference to the source component of the
    association.

    There is one additional field:

     * `target_component_id` - SCTID of the destination component of the
     association

    ### Module dependency reference sets
    The `refset_id` should be set to one of the descendants ( children ) of
    <http:/terminology/concepts/900000000000534007/>.

    The `referenced_component_id` is an SCTID - for a module that the subject
    module of this refset entry is dependent upon.

    There are two additional fields:

     * `source_effective_time` - <a date, in YYYYMMDD ISO-8601 format>
     * `target_effective_time` - <a date, in YYYYMMDD ISO-8601 format>

    The two fields above tie down the dependency to specific versions.

    ### Description format reference sets
    The `refset_id` should be set to one of the descendants ( children ) of
    <http:/terminology/concepts/900000000000538005/>.

    The `referenced_component_id` should be a descendant of
    <http:/terminology/concepts/900000000000446008/>.

    The refset has the following additional fields:

     * `description_format` - set to a descendant of
     <http:/terminology/concepts/900000000000539002>
     * `description_length` - an integer, specifying the maximum length of the
     subject description, in **bytes**

    ### Reference set descriptor reference sets
    The `refset_id` should be set to one of the descendants ( children ) of
    <http:/terminology/concepts/900000000000456007/>.

    The `referenced_component_id` should be set to one of the descendants of
    <http:/terminology/concepts/900000000000455006/>.

    Include in the JSON payload the following additional fields:

     * `attribute_description` - set to a descendant of
     <http:/terminology/concepts/900000000000457003/>
     * `attribute_type` - set to a descendant of
     <http:/terminology/concepts/900000000000459000/>
     * `attribute_order` - position of the described attribute, where "0" is
     the `referenced_component_id`

    The manner in which this reference set type is used will surprise the
    unwary - **an entry is created for each attribute in the reference set that
    is to be described**. The `attribute_order` field defines the order of
    appearance of the additional attributes.

    # Updating reference set content
    In order to update a reference set **member**, issue a `PUT` request to the
    same URLs used for creation, with the same payload formats.

    # Inactivating reference set content
    In order to inactivate a reference set **member**, issue a `DELETE' request
    to:

    ```
    /terminology/refset/inactivate/<refset_sctid>/<entry_uuid>/
    ```
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
        # Simpler to add detail URL here
        # It applies to all reference set types ( different ModelSerializers )
        for item in serializer.data['results']:
            item['detail_url'] = reverse(
                'terminology:refset-detail',
                kwargs={
                    'refset_id': str(item['refset_id']),
                    'entry_id': str(item['row_id'])
                },
                request=request
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
        # We want fully qualified URLs; so we need a request
        # Hence the location of this code
        for item in serializer.data['results']:
            item['detail_url'] = reverse(
                'terminology:description-detail',
                kwargs={
                    'component_id': str(item['component_id'])
                },
                request=request
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
        # We want fully qualified URLs; so we need a request
        # Hence the location of this code
        for item in serializer.data['results']:
            item['detail_url'] = reverse(
                'terminology:relationship-detail',
                kwargs={
                    'component_id': str(item['component_id'])
                },
                request=request
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

    In order to obtain release information ( current and past ), issue a `GET`
    to `/terminology/admin/release/`.

    In order to create a new module, `POST` to `/terminology/admin/namespace`
    a JSON payload of the following form:

        {
            "effective_date": <an ISO-8601 [ YYYYMMDD ] string>,
            "fully_specified_name": <the new module's FSN>,
            "preferred_term": <the new module's PT>,
            "module_id": <optional; SCTID of parent module"
        }

    """
    @detail_route(methods=['get'])
    def releases(self, request):
        """Information about the current and past releases

        Release information is held in the root concept in the following
        manner:

         * the root concept has a current synonym that contains information
         about the release
         * the synonyms representing earlier release are distributed as
         inactive descriptions

        The syntax is as follows:

         * Example: SNOMED Clinical Terms version: 20020131 [R] (first release)
         * Syntax: SNOMED Clinical Terms version: yyyymmdd [status] (descr.)
           * yyyymmdd is the release date, in ISO format
           * status is one of R (release), D (developmental), E (evaluation)
           * descr. is an **optional** free text description
        """
        # Every concept's denormalized view includes inactive descriptions
        root = ConceptDenormalizedView.objects.get(concept_id=138875005)
        descriptions = [
            root_description.replace('SNOMED Clinical Terms version: ', '')
            for root_description in root.descriptions_list_shortened
            if 'SNOMED Clinical Terms version: ' in root_description
        ]
        releases = sorted([
            {
                'release_date': parser.parse(description[0:8]),
                'release_status': RELEASE_STATUSES[description[10]],
                'release_description': description[14:-1]
            } for description in descriptions
        ], key=itemgetter('release_date'), reverse=True)
        return Response(releases)

    @detail_route(methods=['get'])
    def namespace(self, request):
        """Return a map that has this server's namespace and its modules"""
        namespace_id = settings.SNOMED_NAMESPACE_IDENTIFIER
        module_parent_id = 900000000000443000
        all_module_ids = ConceptDenormalizedView.objects.get(
            concept_id=module_parent_id
        ).is_a_children_ids
        this_namespace_module_ids = filter(
            lambda module_id:  str(namespace_id) in str(module_id),
            all_module_ids
        )
        result_map = {
            "namespace": namespace_id,
            "modules": [
                {
                    "module_id": module_id,
                    "detail_url": reverse(
                        'terminology:concept-detail-short',
                        kwargs={'concept_id': str(module_id)},
                        request=request
                    )
                }
                for module_id in this_namespace_module_ids
            ]
        }
        return Response(result_map)

    @detail_route(methods=['get'])
    def export(self, request):
        # TODO If a namespace ID is not given, export this server's namespace
        # TODO Work out a format that can be processed by the load tools
        # TODO Export also our namespace control table
        pass

    @detail_route(methods=['get'])
    def build(self, request):
        """Make changes made since the last build 'available for use'"""
        # TODO Check for changes in any module and update effective_time
        # TODO Add to docs warning about effect of build ( new records )
        chain(refresh_dynamic_snapshot, refresh_materialized_views)
        return Response({"status": "OK"})

    @list_route(methods=['post'])
    def create_module(self, request):
        """Create a module in this terminology server's namespace

        {
            "effective_date": <an ISO-8601 string>,
            "fully_specified_name": <the new module's FSN>,
            "preferred_term": <the new module's PT>,
            "module_id": <optional; SCTID of parent module"
        }

        """
        # Enforce invariants in the passed in data structure
        data = request.DATA
        for f in ['effective_date', 'fully_specified_name', 'preferred_term']:
            if f not in data:
                raise TerminologyAPIException('%s field missing' % f)

        # Parse the input that needs parsing
        try:
            effective_date = parser.parse(data['effective_date'])
        except:
            # Yes, this is usually the stupid way to catch exceptions
            # Forced by the limitations of dateutil.parser ( third party )
            # They do not wrap the "raw" Python errors
            raise TerminologyAPIException(
                'Cannot parse %s into a date' % data['effective_date'])

        # Extract the optional module_id and confirm that it is a valid module
        if 'module_id' in data:
            _confirm_concept_descends_from(
                data['module_id'], 900000000000443000)
            user_module_id = data['module_id']
        else:
            user_module_id = None

        ## The concept record
        new_concept_id = _allocate_new_component_id('CONCEPT')
        module_id = new_concept_id if not user_module_id else user_module_id
        new_concept = ConceptFull(
            component_id=new_concept_id,
            module_id=module_id,
            active=True,
            definition_status_id=900000000000073002,  # Defined
            effective_time=effective_date
        )

        ## The fully specified name
        new_fsn_id = _allocate_new_component_id('DESCRIPTION')
        new_fsn = DescriptionFull(
            component_id=new_fsn_id,
            module_id=module_id,
            active=True,
            effective_time=effective_date,
            concept_id=new_concept_id,
            language_code='en',
            type_id=900000000000003001,  # Fully specified name
            case_significance_id=900000000000017005,  # Case sensitive
            term=data['fully_specified_name']
        )

        ## The preferred term
        new_pt_id = _allocate_new_component_id('DESCRIPTION')
        new_pt = DescriptionFull(
            component_id=new_pt_id,
            module_id=module_id,
            active=True,
            effective_time=effective_date,
            concept_id=new_concept_id,
            language_code='en',
            type_id=900000000000013009,  # Synonym
            case_significance_id=900000000000017005,  # Case sensitive
            term=data['preferred_term']
        )

        ## Language reference set entry for preferred term
        lang_refset_pt_row_id = uuid.uuid4()
        new_lang_refset_pt_row = LanguageReferenceSetFull(
            row_id=lang_refset_pt_row_id,
            effective_time=effective_date,
            active=True,
            module_id=module_id,
            refset_id=900000000000508004,  # UK Language Reference Set,
            referenced_component_id=new_pt.component_id,
            acceptability_id=900000000000548007  # Preferred
        )

        ## Language reference set entry for fully specified name
        lang_refset_fsn_row_id = uuid.uuid4()
        new_lang_refset_fsn_row = LanguageReferenceSetFull(
            row_id=lang_refset_fsn_row_id,
            effective_time=effective_date,
            active=True,
            module_id=module_id,
            refset_id=900000000000508004,  # UK Language Reference Set,
            referenced_component_id=new_fsn.component_id,
            acceptability_id=900000000000549004  # Acceptable
        )

        ## Relationships ( |is a| )
        new_relationship_id = _allocate_new_component_id('RELATIONSHIP')
        rel_dest = 900000000000443000 if not user_module_id else user_module_id
        new_relationship = RelationshipFull(
            component_id=new_relationship_id,
            module_id=module_id,
            active=True,
            effective_time=effective_date,
            source_id=new_concept_id,
            destination_id=rel_dest,  # module_id determined above
            relationship_group=0,
            type_id=116680003,  # |is a|
            characteristic_type_id=900000000000010007,  # |stated relationship|
            modifier_id=900000000000451002  # |some| ; SNOMED description logic
        )

        ## We want these to all succeed or all fail
        with transaction.atomic():
            new_concept.save()
            new_fsn.save()
            new_pt.save()
            new_lang_refset_fsn_row.save()
            new_lang_refset_pt_row.save()
            new_relationship.save()

        ## Compose the return message
        return Response({
            'message': 'Created; queue a build before you use the module',
            'module_concept_id': new_concept.component_id,
            'module_fully_specified_name_id': new_fsn.component_id,
            'module_preferred_term_id': new_pt.component_id,
            'module_fsn_lang_refset_row_id':
            str(new_lang_refset_fsn_row.row_id),
            'module_pt_lang_refset_row_id':
            str(new_lang_refset_pt_row.row_id),
            'build_url': reverse('terminology:build', request=request)
        })
