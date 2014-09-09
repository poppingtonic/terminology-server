import logging

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.decorators import detail_route, list_route

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from core.models import ConceptDenormalizedView
from core.models import DescriptionDenormalizedView
from core.models import RelationshipDenormalizedView

from .serializers import ConceptReadShortenedSerializer
from .serializers import ConceptReadFullSerializer
from .serializers import ConceptSubsumptionSerializer
from .serializers import ConceptReadPaginationSerializer
from .serializers import DescriptionReadSerializer
from .serializers import DescriptionReadPaginationSerializer
from .serializers import RelationshipReadSerializer
from .serializers import RelationshipReadPaginationSerializer

LOGGER = logging.getLogger(__name__)


class TerminologyAPIException(APIException):
    """Communicate errors that arise from wrong params to terminology APIs"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Wrong request format'


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
        try:
            concepts = ConceptDenormalizedView.objects.filter(
                concept_id=concept_id)
            serializer = ConceptReadShortenedSerializer \
                if representation_type == 'shortened' \
                else ConceptReadFullSerializer
            return Response(serializer(concepts, many=True).data)
        except ConceptDenormalizedView.DoesNotExist:
            raise TerminologyAPIException(
                'There is no concept with SCTID %s' % concept_id)

    def list(self, request):
        """Paginated list of concepts
        :param request:
        """
        queryset = ConceptDenormalizedView.objects.all()
        serializer = ConceptReadPaginationSerializer(
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
        # TODO Validate the module id
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

    @detail_route(methods=['get'])
    def release(self, request):
        """Information about the current release"""
        pass

    @list_route(methods=['get'])
    def releases(self, request):
        """Information about all the releases known to this server"""
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
        pass

    def list(self, request, refset_id, module_id=None):
        """Paginated listing of refset conctent
        :param request:
        :param refset_id: identifies the reference set that is to be listed
        :param module_id: ( optional ) filter by the module entries belong to

        If the `module_id` is not supplied, all applicable refset content will
        be listed.
        """
        # TODO Obtain all the descendants of simple reference set
        # TODO Apply module_id filter
        # TODO Paginate queryset
        pass

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
        try:
            descriptions = DescriptionDenormalizedView.objects.filter(
                component_id=component_id
            )
            return Response(
                DescriptionReadSerializer(descriptions, many=True).data
            )
        except DescriptionDenormalizedView.DoesNotExist:
            raise TerminologyAPIException(
                'There is no description with SCTID %s' % component_id)

    def list(self, request):
        """Paginated listing of descriptions

        :param request:
        """
        queryset = DescriptionDenormalizedView.objects.all()
        serializer = DescriptionReadPaginationSerializer(
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
        try:
            relationships = RelationshipDenormalizedView.objects.filter(
                component_id=component_id
            )
            return Response(
                RelationshipReadSerializer(relationships, many=True).data
            )
        except RelationshipDenormalizedView.DoesNotExist:
            raise TerminologyAPIException(
                'There is no relationship with SCTID %s' % component_id)

    def list(self, request):
        """Paginated listing of relationships

        :param request:
        """
        queryset = RelationshipDenormalizedView.objects.all()
        serializer = RelationshipReadPaginationSerializer(
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
    """Perform administrative tasks and introspect the server's data"""
    @detail_route(methods=['get'])
    def get(self, request):
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
        pass
