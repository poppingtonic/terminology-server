from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import APIException

from core.models import ConceptDenormalizedView

from .serializers import ConceptReadShortenedSerializer
from .serializers import ConceptReadFullSerializer

import logging

LOGGER = logging.getLogger(__name__)


class TerminologyAPIException(APIException):
    """Communicate errors that arise from wrong params to terminology APIs"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Wrong request format'


class ConceptView(APIView):
    """List / enumerate concepts, including various commonly used hierarchies

    This service should be called with a URL of the form:

    ```
    (URL Prefix)/<concept_id>/<representation_type>/
    ``

    The `representation_type` parameter determines whether a full /
    detailed representation ( resource heavy ) or a lightweight representation
    ( resource light ) is sent. The valid choices for this parameter are:

        * `shortened` - the default, render a bandwidth and CPU/memory saving
        representation; **include only direct parents / children**
        * `full` - render the full denormalized representation
    """
    def _validate_representation_type(self, representation_type):
        if representation_type not in ['shortened', 'full']:
            raise TerminologyAPIException(
                'Unknown representation type: %s' % representation_type)

    # TODO This view might end up proxying to a view that takes a concept ID
    def get(self, request, concept_id=None, representation_type='shortened'):
        """
        :param request:
        :param enumeration_type:
        :param direct_links_only
        :param representation_type
        :return:
        """
        self._validate_representation_type(representation_type)
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

# TODO Pagination - nested pagination within the concepts themselves
# TODO List endpoints for concepts, descriptions, relationships
# TODO Special endpoint for release information - current, historical
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
