import datetime
import psycopg2
from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from ..utils import (parse_date_param,
                     as_bool,
                     execute_query,
                     _positive_int)

from snomedct_terminology_server.server.models import (
    Concept,
    LanguageReferenceSetDenormalizedView
)

from snomedct_terminology_server.server.search import WordEquivalentMixin

from snomedct_terminology_server.server.apps import ServerConfig

from snomedct_terminology_server.server.views.core_views import releases

from snomedct_terminology_server.server.views import (ListConcepts,
                                                      generate_refset_list_view)

from snomedct_terminology_server.server.serializers import (
    serialized_refset,
    REFSET_MODELS)


class UnitTests(TestCase):
    def test_as_bool(self):
        default1 = False
        default2 = True
        var1 = 'false'
        var2 = 'false'
        assert as_bool(var1, default1) is False
        assert as_bool(var2, default2) is False

        var1 = 'true'
        var2 = 'true'
        assert as_bool(var1, default1) is True
        assert as_bool(var2, default2) is True

        var1 = 'some crap'
        try:
            assert as_bool(var1, default1) is False
        except Exception as ex:
            assert str(ex) == """You requested a resource with ?active=some crap, which is not a boolean type. Depending on what you need, use ?active=True or ?active=False."""  # noqa

        var1 = '"{}"'
        try:
            assert as_bool(var1, default1) is False
        except Exception as ae:
            assert isinstance(ae, AssertionError)

        var1 = None
        assert as_bool(var1) is True

        assert as_bool(False) is False

        assert as_bool(None) is True

    def test_date_parser(self):
        date = '2016-01-31'
        assert parse_date_param(date, from_filter=True) == datetime.date(2016, 1, 31)

    def test_concept_repr(self):
        concept = Concept.objects.get(id=6122008)
        assert concept.__str__() == '6122008 | Class Ia antiarrhythmic drug (substance) |'

    def test_apps(self):
        assert ServerConfig.name == 'server'

    def test_execute_query(self):
        concept_id = 6122008
        query = """select preferred_term from \
snomed_denormalized_concept_view_for_current_snapshot where id = %s"""
        assert execute_query(query, concept_id) == 'Class Ia antiarrhythmic drug (substance)'

        malformed_query = """selct preferred_term from
snomed_denormalized_concept_view_for_current_snapshot where id = 6122008"""
        with self.assertRaises(APIException):
            with self.assertRaises(psycopg2.ProgrammingError):
                execute_query(malformed_query)

    def test_releases(self):
        current_release = {
            "release_description": "January 2016 Release",
            "release_date": "2016-01-31",
            "release_status": "Released"}
        assert releases(release_type='international_release')[0] == current_release
        assert 'UK drug extension' in releases(release_type='drug_extension')
        assert 'UK clinical extension' in releases(release_type='clinical_extension')

        with self.assertRaises(APIException):
            releases(release_type='foobar')

    def test_common_search_filter(self):
        factory = APIRequestFactory()
        view = generate_refset_list_view(
            LanguageReferenceSetDenormalizedView
        ).as_view()

        request = factory.get('/terminology/refset/language/',
                              {'search': 'united states of america'})
        response = view(request).render()
        assert response.status_code == status.HTTP_200_OK

    def test_serialized_refset(self):
        factory = APIRequestFactory()
        request = factory.get('/terminology/refset/language/')

        model = REFSET_MODELS['LANGUAGE']
        serializer = serialized_refset(model)

        model_instance = model.objects.first()
        data = serializer(model_instance, context={'request': Request(request)}).data
        assert data['id'] == str(model_instance.id)

    def test_serializer_to_representation(self):
        view = ListConcepts.as_view()
        factory = APIRequestFactory()
        request = factory.get('/terminology/concepts/',
                              {'fields': 'reference_set_memberships'})

        response = view(request).render()
        assert 'reference_set_memberships' in response.data['results'][0].keys()

    def test_positive_int(self):
        assert _positive_int('13') == 13
        with self.assertRaises(ValueError):
            _positive_int('foo')
            _positive_int('-32')
            _positive_int('0')

    def test_word_equivalent_mixin(self):
        word = 'weekly'
        we = WordEquivalentMixin()
        equivalents = we.get_word_equivalents(word)
        assert equivalents == [word]
