from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.decorators import detail_route, list_route

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from core.models import ConceptDenormalizedView

from .serializers import ConceptReadShortenedSerializer
from .serializers import ConceptReadFullSerializer
from .serializers import ConceptSubsumptionSerializer
from .serializers import ConceptReadPaginationSerializer

import logging

LOGGER = logging.getLogger(__name__)


class TerminologyAPIException(APIException):
    """Communicate errors that arise from wrong params to terminology APIs"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Wrong request format'


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
            concept = ConceptDenormalizedView.objects.get(
                concept_id=concept_id)
            serializer = ConceptReadShortenedSerializer \
                if representation_type == 'shortened' \
                else ConceptReadFullSerializer
            return Response(serializer(concept).data)
        except ConceptDenormalizedView.DoesNotExist:
            raise TerminologyAPIException(
                'There is no concept with SCTID %s' % concept_id)

    def list(self, request):
        """Paginated list of concepts
        :param request:
        """
        queryset = ConceptDenormalizedView.objects.all()
        paginator = Paginator(
            queryset, settings.REST_FRAMEWORK['PAGINATE_BY'])
        page = request.QUERY_PARAMS.get('page')

        try:
            concepts = paginator.page(page)
        except PageNotAnInteger:
            concepts = paginator.page(1)
        except EmptyPage:
            concepts = paginator.page(paginator.num_pages)

        serializer_context = {'request': request}
        serializer = ConceptReadPaginationSerializer(
            concepts, context=serializer_context)
        return Response(serializer.data)

    def create(self, request):
        pass

    def update(self, request, concept_id):
        pass

    def destroy(self, request, concept_id):
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
                'There is no concept with SCTID %s' % concept_id)\



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
    # TODO Implement in full
    pass


class DescriptionView(viewsets.ViewSet):
    def retrieve(self, request, component_id):
        # TODO Implement list endpoint
        pass

    def list(self, request):
        pass

    def create(self, request):
        pass

    def update(self, request, concept_id):
        pass

    def destroy(self, request, concept_id):
        pass


class RelationshipView(viewsets.ViewSet):
    def retrieve(self, request, component_id):
        # TODO Implement list endpoint
        pass

    def list(self, request):
        pass

    def create(self, request):
        pass

    def update(self, request, concept_id):
        pass

    def destroy(self, request, concept_id):
        pass


class AdminView(viewsets.ViewSet):
    """Perform administrative tasks and introspect the server's data"""
    @detail_route(methods=['get'])
    def get(self, request):
        # TODO return a map that has this server's namespace and its modules
        pass

    @detail_route(methods=['get'])
    def export(self, request, namespace_identifier=None):
        # TODO If a namespace ID is not given, export this server's namespace
        # TODO Work out a format that can be processed by the load tools
        pass

    @detail_route(methods=['get'])
    def build(self, request):
        # TODO Queue a build then return a success message
        pass
