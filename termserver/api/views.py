from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import link
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from core.models import ConceptDenormalizedView

from .serializers import ConceptReadSerializer


class ReleaseInformationViewSet(viewsets.ViewSet):
    """
    Get info about the SNOMED CT Releases on this terminology server
    """
    def list(self, request):
        """Listing of all known SNOMED releases ( most recent first )"""
        pass

    @link()
    def current(self, request):
        """Return information pertaining to the current SNOMED release"""
        pass


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


class ConceptReadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ConceptDenormalizedView.objects.all()
    serializer_class = ConceptReadSerializer

# TODO All list endpoints should support the parameter "direct_links_only" ( default False, set to True to see only direct children )
# TODO /terminology/concepts/root/
# TODO /terminology/concepts/top_level/ ( descendants of the top level concept )
# TODO /terminology/concepts/is_a/ ( 116680003 )
# TODO /terminology/concepts/metadata/ ( 900000000000441003 - model component )
# TODO /terminology/concepts/medatata/core/ ( 900000000000442005 - core metadata concept )
# TODO /terminology/concepts/metadata/foundation/ ( 900000000000454005 - foundation metadata concept )
# TODO /terminology/concepts/refsets/ ( 900000000000455006 )
# TODO /terminology/concepts/attributes/ ( 246061005 - attributes / linkage concepts )
# TODO /terminology/concepts/reltypes/ ( 410662002 - relationship types )
# TODO /terminology/concepts/namespaces/ ( 370136006 )
# TODO /terminology/concepts/navigational/ ( 363743006 )
# TODO /terminology/concepts/reference_sets/ ( 900000000000455006 )


# TODO /terminology/module_identifiers/ ( 900000000000443000 )
# TODO /terminology/definition_status_identifiers/ ( 900000000000444006 )
# TODO /terminology/description_type_identifiers/ ( 900000000000446008 )
# TODO /terminology/case_significance_identifiers/ ( 900000000000447004 )
# TODO /terminology/characteristic_type_identifiers/ ( 900000000000449001 )
# TODO /terminology/modifier_identifiers/ ( 900000000000450001 )
# TODO /terminology/identifier_scheme_identifiers/ ( 900000000000453004 )
# TODO /terminology/attribute_value_identifiers/ ( 900000000000491004 )
# TODO /terminology/reference_set_descriptor_identifiers/ ( 900000000000456007 )

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
