from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import APIException

from core.models import ConceptDenormalizedView

from .serializers import ConceptReadShortenedSerializer
from .serializers import ConceptReadFullSerializer
from .serializers import ConceptSubsumptionSerializer

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
    (URL Prefix)/concepts/<concept_id>/<representation_type>/
    ```

    The `representation_type` parameter determines whether a full /
    detailed representation ( resource heavy ) or a lightweight representation
    ( resource light ) is sent. The valid choices for this parameter are:

        * `shortened` - the default, render a bandwidth and CPU/memory saving
        representation; **include only direct parents / children**
        * `full` - render the full denormalized representation

    TODO - document shortcut URLs
    """
    def get(self, request, concept_id=None, representation_type='shortened'):
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


class SubsumptionView(APIView):
    """Identify a concept's parents, ancestors, children, descendants

    This service should be called with a URL of the form:

    ```
    (URL Prefix)/subsumption/<concept_id>/
    ```
    """
    def get(self, request, concept_id=None, representation_type='shortened'):
        """
        :param request:
        :param enumeration_type:
        :param direct_links_only
        :param representation_type
        :return:
        """
        try:
            concept = ConceptDenormalizedView.objects.get(
                concept_id=concept_id)
            return Response(ConceptSubsumptionSerializer(concept).data)
        except ConceptDenormalizedView.DoesNotExist:
            raise TerminologyAPIException(
                'There is no concept with SCTID %s' % concept_id)\



class RefsetView(APIView):
    """Create, retrieve, update and inactivate reference set members

    This API does not facilitate the creation of new reference set types.

    The general URL form is:

    ```
    (URL Prefix)/refset/<refset_sctid>/
    ```

    The following **shortcut** URLs shall be defined:
        * `(URL Prefix)/refset/simple/`
        * `(URL Prefix)/refset/ordered/`
        * `(URL Prefix)/refset/attribute_value/`
        * `(URL Prefix)/refset/simple_map/`
        * `(URL Prefix)/refset/complex_map/`
        * `(URL Prefix)/refset/extended_map/`
        * `(URL Prefix)/refset/language/`
        * `(URL Prefix)/refset/query_specification/`
        * `(URL Prefix)/refset/annotation/`
        * `(URL Prefix)/refset/association/`
        * `(URL Prefix)/refset/module_dependency/`
        * `(URL Prefix)/refset/description_format/`

    Reference sets may be filtered by `module_id` as follows:

    ```
    (URL Prefix)/refset/<refset_sctid>/<module_id>/
    ```

    This filtering pattern will also work with the shortcuts defined above.
    For example:
        * `(URL Prefix)/refset/simple/<module_id>/`
        * ...the same pattern for all other shortcuts...
    """
    # TODO Implement in full
    pass

# TODO List endpoints for concepts, descriptions, relationships
# TODO Special endpoint for release information - current, historical

# TODO /terminology/representation/<concept id>/
# TODO /terminology/representation/equivalents/
# TODO /terminology/representation/subsumed/
# TODO /terminology/normalization/long/<concept id>/
# TODO /terminology/normalization/short/<concept id>/
# TODO /terminology/expressions/repository/
# TODO /terminology/expressions/

# TODO Listing the modules that belong to a namespace **
# TODO Retrieve this terminology server's namespace
# TODO List the modules that belong to this terminology server's namespace
# TODO /terminology/authoring/concepts/
# TODO /terminology/authoring/concepts/<concept id>/ ( include inactivate )
# TODO /terminology/authoring/descriptions/
# TODO /terminology/authoring/descriptions/<description id>/ ( include inactivate )
# TODO /terminology/authoring/relationships/
# TODO /terminology/authoring/relationships/relationship id>/ ( include inactivate )


# TODO /terminology/export/module/<module SCTID>/
# TODO /terminology/export/refset/<refset UUID>/
# TODO /terminology/export/namespace/<namespace identifier>/
# TODO /terminology/build/
