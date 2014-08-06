from rest_framework import viewsets
from rest_framework.decorators import link


# TODO Use DRF named status codes and status helpers e.g is_error(); from rest_framework import status

class ReleaseInformationViewSet(viewsets.ViewSet):
    """
    Obtain information about the SNOMED CT International Releases on this terminology server
    """
    def list(self, request):
        """Return a listing of all known SNOMED releases, in reverse chronological order ( most recent first )"""
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
