from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import link
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import APIException

from core.models import ConceptDenormalizedView

from .serializers import ConceptReadShortenedSerializer
from .serializers import ConceptReadFullSerializer

# Facilitates listing of direct children or descendants of key concepts
ENUMERATION_TYPES = {
    'root': 138875005,
    'is_a': 116680003,
    'core_metadata': 900000000000441003,
    'foundation_metadata': 900000000000454005,
    'reference_sets': 900000000000455006,
    'attributes': 246061005,
    'relationship_types': 410662002,
    'namespaces': 410662002,
    'navigational': 363743006,
    'module_identifiers': 900000000000443000,
    'definition_status_identifiers': 900000000000444006,
    'description_type_identifiers': 900000000000446008,
    'case_significance_identifiers': 900000000000447004,
    'characteristic_type_identifiers': 900000000000449001,
    'modifier_identifiers': 900000000000450001,
    'identifier_scheme_identifiers': 900000000000453004,
    'attribute_value_identifiers': 900000000000491004,
    'reference_set_descriptor_identifiers': 900000000000456007
}


class TerminologyAPIException(APIException):
    """Communicate errors that occur during search"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Wrong request format'


class DescriptionViewSet(viewsets.ViewSet):
    def list(self, request):
        pass

    def retrieve(self, request, component_id=None):
        """Retrieve a single description, using it's component ID"""
        pass

    @link()
    def concept(self, request, concept_sctid=None):
        """Retrieve the descriptions that are associated with a concept"""
        pass

# TODO Special endpoint for release information - current, historical


class ConceptReadView(APIView):
    """List / enumerate concepts, including various commonly used hierarchies

    This service should be called with a URL of the form:

    ```
    (URL Prefix)/<enumeration_type>/<representation_type>/<direct_links_only>/
    ```

    The first parameter ( `enumeration_type` ) determines the SNOMED tree that
    will be serialized. It defaults to `all` ( enumerate the entire SNOMED
    hierarchy ). The valid choices for this parameter are:

        * `root` - display information about the root concept,
        including its direct / indirect children
        * `core_metadata` - a listing of core metadata concepts
        ( enumerated values applicable to core components )
        * `foundation_metadata` - a listing of foundation metadata concepts
        ( reference sets and their metadata )
        * `reference_sets` - a listing of known reference sets
        * `attributes` - a listing of attributes that may be applied to models
        * `relationship_types` - a listing of they valid relationship types
        e.g |is a|
        * `namespaces` - a listing of namespaces issued to organizations that
        can author terminologies
        * `navigational` - a listing of concepts whose role is purely
        navigational
        * `module_identifiers` - a listing of known modules
        * `definition_status_identifiers` - a listing of valid definition
        statuses
        * `description_type_identifiers` - a listing of valid description
        type identifiers
        * `case_significance_identifiers` - a listing of valid case
        significance identifiers
        * `characteristic_type_identifiers` - a listing of valid characteristic
        type identifiers
        * `modifier_identifiers` - a listing of valid modifiers
        * `identifier_scheme_identifiers` - a listing of valid identifier
        schemes
        * `attribute_value_identifiers` - a listing of valid attribute values
        * `reference_set_descriptor_identifiers` - a listing of valid reference
        set descriptors

    The second parameter ( `representation_type` ) determines whether a full /
    detailed representation ( resource heavy ) or a lightweight representation
    ( resource light ) is sent. The valid choices for this parameter are:

        * `shortened` - the default, render a bandwidth and CPU/memory saving
        representation; include only direct parents / children
        * `full` - render the full denormalized representation

    The third parameter ( `direct_links_only` ) determines whether the
    serializer should include only direct parents and children ( the default )
    or all parents / ancestors and children / descendants. It defaults to `all`
    and should generally be left that way ( serializing all children of a
    concept that is near the root of the hierarchy can be very expensive ). The
    valid choices for this parameter are:

        * `true` - include only direct parents and direct children
        * `false` - the default; include all parents / ancestors and all
        children / descendants.
    """
    def _validate_enumeration_type(self, enumeration_type):
        if enumeration_type not in ['root'] + list(ENUMERATION_TYPES.keys()):
            raise TerminologyAPIException(
                'Unknown enumeration type: %s' % enumeration_type)

    def _validate_representation_type(self, representation_type):
        if representation_type not in ['shortened', 'full']:
            raise TerminologyAPIException(
                'Unknown representation type: %s' % representation_type)

    def _validate_direct_links_only_param(self, direct_links_only):
        if direct_links_only not in ['true', 'false']:
            raise TerminologyAPIException(
                'Unknown `direct_links_only` param: %s' % direct_links_only)

    def get(self, request, enumeration_type='root',
            representation_type='shortened', direct_links_only='false'):
        """
        :param request:
        :param enumeration_type:
        :param direct_links_only
        :param representation_type
        :return:
        """
        # Sanity checks
        self._validate_enumeration_type(enumeration_type)
        self._validate_representation_type(representation_type)
        self._validate_direct_links_only_param(direct_links_only)

        # A single special case for listing of the root concept
        parent_concept_id = ENUMERATION_TYPES[enumeration_type]
        try:
            concept = ConceptDenormalizedView.objects.get(
                concept_id=parent_concept_id)
            serializer = ConceptReadShortenedSerializer \
                if representation_type == 'shortened' \
                else ConceptReadFullSerializer
            # TODO Processing of direct_links_only
            return Response(serializer(concept))
        except ConceptDenormalizedView.ObjectDoesNotExist:
            raise TerminologyAPIException(
                'There is no concept with SCTID %s' % parent_concept_id)

        # TODO Pagination

# TODO /terminology/concepts/root/


# TODO /terminology/subsumption/parents/<concept id>/?full=true|false
# TODO /terminology/subsumption/ancestors/<concept id>/?full=true|false
# TODO /terminology/subsumption/children/<concept id>/?full=true|false
# TODO /terminology/subsumption/descendants/<concept id>/?full=true|false

# TODO /terminology/representation/<concept id>/
# TODO /terminology/representation/equivalents/
# TODO /terminology/representation/subsumed/
# TODO /terminology/normalization/long/<concept id>/
# TODO /terminology/normalization/short/<concept id>/
# TODO /terminology/expressions/repository/
# TODO /terminology/expressions/

# TODO /terminology/authoring/concepts/
# TODO /terminology/authoring/concepts/<concept id>/
# TODO /terminology/authoring/concepts/<concept id>/
# TODO /terminology/authoring/descriptions/
# TODO /terminology/authoring/descriptions/<description id>/
# TODO /terminology/authoring/relationships/
# TODO /terminology/authoring/relationships/relationship id>/

# TODO /terminology/refsets/<refset member uuid>/ - inactivate
# TODO /terminology/refsets/<refset UUID>/
# TODO /terminology/refsets/simple/
# TODO /terminology/refsets/ordered/
# TODO /terminology/refsets/attribute_value/
# TODO /terminology/refsets/simple_map/
# TODO /terminology/refsets/complex_map/
# TODO /terminology/refsets/extended_map/
# TODO /terminology/refsets/language/
# TODO /terminology/refsets/query_specification/
# TODO /terminology/refsets/annotation/
# TODO /terminology/refsets/association/
# TODO /terminology/refsets/module_dependency/
# TODO /terminology/refsets/description_format/

# TODO /terminology/export/module/<module SCTID>/
# TODO /terminology/export/refset/<refset UUID>/
# TODO /terminology/export/namespace/<namespace identifier>/

# TODO /terminology/build/
