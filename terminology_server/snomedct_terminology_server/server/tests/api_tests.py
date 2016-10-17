from collections import OrderedDict
from itertools import islice, chain
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.request import Request
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter

from snomedct_terminology_server.server.models import (
    Concept,
    Description,
    LanguageReferenceSetDenormalizedView
)

from snomedct_terminology_server.server.search import CommonSearchFilter
from snomedct_terminology_server.server.views import (
    ListConcepts,
    current_release_information,
    historical_release_information)

from snomedct_terminology_server.server.serializers import DescriptionListSerializer


class TestConcept(APITestCase):
    def test_concept_list(self):
        response = self.client.get('/terminology/concepts/')
        assert response.status_code == 200
        assert len(response.data['results'][0].keys()) == 12

        assert 'url' in response.data['results'][0].keys()

        response = self.client.get('/terminology/concepts/?fields=reference_set_memberships')
        assert response.status_code == 200
        assert len(response.data['results'][0].keys()) == 1
        assert 'reference_set_memberships' in response.data['results'][0].keys()

    def test_concept_list_by_id(self):
        response = self.client.post('/terminology/concept_list_by_id/',
                                    data={'sctid_list': '11959009,31306009,76759004,318259005'})
        assert response.status_code == 200
        assert len(response.data) == 4

        response = self.client.post('/terminology/concept_list_by_id/',
                                    data={'sctid_list': 'foobar,quuxmeta'})
        assert response.status_code == 500
        assert 'detail' in response.data.keys()

        response = self.client.post('/terminology/concept_list_by_id/',
                                    data={'objects': 'foobar,quuxmeta'})
        assert response.status_code == 500
        assert 'detail' in response.data.keys()

    def test_concept_list_release_date(self):
        response = self.client.get('/terminology/concepts/?release_date=2016-01-31')
        assert response.status_code == 200
        assert '6122008' in response.data['results'][0]['url']

    def test_concept_detail(self):
        response = self.client.get('/terminology/concept/6122008/')
        assert response.data['preferred_term'] == "Class Ia antiarrhythmic drug"

    def test_concept_nested_field_detail(self):
        response = self.client.get(
            '/terminology/concept/6122008/?fields=preferred_term,incoming_relationships.source_name'
        )
        assert response.data['preferred_term'] == "Class Ia antiarrhythmic drug"

        response = self.client.get(
            '/terminology/concept/76759004/?fields=preferred_term,reference_set_memberships.refset_name'  # noqa
        )
        assert response.data['preferred_term'] == "Disopyramide (product)"
        assert len(response.data['reference_set_memberships']) == 0

        response = self.client.get(
            '/terminology/concept/6122008/?fields=preferred_term,reference_set_memberships.refset_name'  # noqa
        )
        assert "CTV3 simple map" in chain.from_iterable(
            [list(x.values())
             for x in response.data['reference_set_memberships']])
        assert len(response.data['reference_set_memberships'][0].keys()) == 1

        response = self.client.get(
            '/terminology/concept/6122008/?fields=preferred_term,incoming_relationships.foobar'
        )
        assert 'detail' in response.data.keys()

        response = self.client.get(
            '/terminology/concept/6122008/?fields=preferred_term,incoming_foobar.relationships'
        )
        assert 'detail' in response.data.keys()

        response = self.client.get(
            '/terminology/concept/6122008/?fields=preferred_term,fully_specified_name.relationships'
        )
        assert 'detail' in response.data.keys()

    def test_concept_search(self):
        """" This includes test-cases for the spelling-correction quality
improvements. This tests for 6 different possible errors:

I use the term 'procainamide' as the correct term to search for.

+ Single-letter substitution: e.g. `procainaimde` or `proacinamide`.

+ Single-letter deletion: e.g. `procanamide` or `prcainamide`.

+ Double-letter deletion: e.g. `procanamie` or `procainade`.

+ Double-letter insertion e.g. `procainamixxde` or `procaiffnamide`

+ Single-letter insertion e.g. `procainamiede` or `procaidnamide`

+ Double-letter substitution e.g. `procaniaimde` or `prcoainamied`

        """
        # should find results for a correctly-spelled term present in the DB
        response = self.client.get('/terminology/concepts/?search=procainamide')
        assert response.status_code == 200

        # should find results for a term present in the DB, if the term
        # is misspelled in the following 6 ways. See the docstring for a
        # description of this mechanism.
        response = self.client.get('/terminology/concepts/?search=procainaimde')
        assert response.status_code == 200

        response = self.client.get('/terminology/concepts/?search=procainade')
        assert response.status_code == 200

        response = self.client.get('/terminology/concepts/?search=prcainamide')
        assert response.status_code == 200

        response = self.client.get('/terminology/concepts/?search=prcoainamied')
        assert response.status_code == 200

        response = self.client.get('/terminology/concepts/?search=procaiffnamide')
        assert response.status_code == 200

        response = self.client.get('/terminology/concepts/?search=procainamiede')
        assert response.status_code == 200

    def test_concept_descendants(self):
        response = self.client.get('/terminology/relationship/descendants/6122008/')
        assert response.status_code == 200
        assert response.data['results'][0]['preferred_term'] == "Procainamide (product)"

        response = self.client.get('/terminology/concepts/metadata/')
        assert response.status_code == 200
        assert response.data['results'] == []

    def test_concept_descendants_search(self):
        response = self.client.get(
            '/terminology/relationship/descendants/6122008/?search=procainamide')
        assert response.status_code == 200
        assert response.data['results'][0]['preferred_term'] == "Procainamide (product)"

        response = self.client.get(
            '/terminology/relationship/descendants/6122008/?search=procainaimde')
        assert response.status_code == 200
        assert response.data['results'][0]['preferred_term'] == "Procainamide (product)"

    def test_concept_children(self):
        response = self.client.get('/terminology/relationship/children/6122008/')
        assert response.status_code == 200
        assert response.data['results'][0]['preferred_term'] == "Procainamide (product)"

    def test_concept_children_search(self):
        response = self.client.get(
            '/terminology/relationship/children/6122008/?search=procainamide')
        assert response.status_code == 200
        assert response.data['results'][0]['preferred_term'] == "Procainamide (product)"

    def test_concept_ancestors(self):
        response = self.client.get('/terminology/relationship/ancestors/11959009/')
        assert response.status_code == 200
        assert response.data['results'][0]['preferred_term'] == "Class Ia antiarrhythmic drug"

    def test_concept_parents(self):
        response = self.client.get('/terminology/relationship/parents/11959009/')
        assert response.status_code == 200
        assert response.data['results'][0]['preferred_term'] == "Class Ia antiarrhythmic drug"
        url = reverse(
            "terminology:list-concept-parents", kwargs={'concept_id': 11959009}
        )
        response = self.client.get(url)
        assert response.data['results'][0]['preferred_term'] == "Class Ia antiarrhythmic drug"

    def test_concept_parents_by_relationship_type(self):
        response = self.client.get('/terminology/relationships/destination_by_type_id/116680003/')
        assert response.status_code == 500
        assert 'detail' in response.data.keys()
        assert len(response.data) == 1

        response = self.client.get(
            '/terminology/relationships/destination_by_type_id/10362601000001103/')
        assert response.status_code == 200
        assert response.data is None

        response = self.client.get(
            '/terminology/relationships/destination_by_type_id/10362701000001108/')
        assert response.status_code == 200
        assert response.data is None

        response = self.client.get('/terminology/relationships/destination_by_type_id/411116001/')
        assert response.status_code == 200
        assert response.data is None


class TestRelationship(APITestCase):
    def test_relationships_list(self):
        response = self.client.get('/terminology/relationships/?format=json')
        assert response.status_code == 200
        assert response.data['results'][0]['destination_name'] =='VMP valid as a prescribable product'  # noqa

    def test_inactive_relationships_list(self):
        response = self.client.get('/terminology/relationships/?format=json&active=false')
        assert response.status_code == 200
        assert response.data['results'][0]['destination_name'] =='Spironolactone 25mg tablet - product'  # noqa

    def test_source_relationships_list(self):
        response = self.client.get(
            '/terminology/relationships/source/8851811000001100/?format=json')
        assert response.status_code == 200
        assert response.data['results'][0]['destination_name'] =='VMP valid as a prescribable product'  # noqa

    def test_destination_relationships_list(self):
        response = self.client.get(
            '/terminology/relationships/destination/8940201000001104/?format=json')
        assert response.status_code == 200
        assert response.data['results'][0]['source_name'] =='EloHaes 6% solution for injection 500ml bags (Fresenius Kabi Ltd) 1 bag'  # noqa

    def test_defining_relationships_list(self):
        response = self.client.get(
            '/terminology/relationships/defining/8851811000001100/?format=json')
        assert response.status_code == 200
        assert response.data['results'][0]['source_name'] =='EloHaes 6% solution for injection 500ml bags (Fresenius Kabi Ltd) 1 bag'  # noqa

    def test_qualifying_relationships_list(self):
        response = self.client.get(
            '/terminology/relationships/qualifying/8851811000001100/?format=json')
        assert response.status_code == 200
        assert len(response.data['results']) == 0

    def test_relationships_detail(self):
        response = self.client.get('/terminology/relationship/100000001000001125/')
        assert response.status_code == 200
        assert response.data['destination_name'] == 'VMP valid as a prescribable product'

        response = self.client.get('/terminology/relationship/100000001000001125/?active=false')
        assert response.status_code == 500
        assert 'detail' in response.data.keys()

    def test_transitive_closure(self):
        response = self.client.get('/terminology/relationships/transitive_closure/')
        assert response.status_code == 200
        assert response.data['results'][0]['subtype_id'] == 11381211000001103

    def test_transitive_closure_ancestors(self):
        response = self.client.get(
            '/terminology/relationships/transitive_closure_ancestors/11420511000001105/')
        assert response.status_code == 200
        assert response.data[0]['supertype_id'] == 317588007

    def test_transitive_closure_descendants(self):
        response = self.client.get(
            '/terminology/relationships/transitive_closure_descendants/317588007/')
        assert response.status_code == 200
        assert response.data[0]['subtype_id'] == 11420511000001105

    def test_transitive_closure_adjacency_list(self):
        response = self.client.get('/terminology/relationships/transitive_closure/adjacency_list/')
        assert response.status_code == 200
        assert 'concept_subsumption.adjlist' in response._headers['content-disposition'][1]


class TestDescription(APITestCase):
    def test_description_list(self):
        response = self.client.get('/terminology/descriptions/')
        assert response.status_code == 200
        assert response.data['results'][0]['type_name'] == 'Synonym'

    def test_single_description(self):
        response = self.client.get('/terminology/description/11168011/')
        assert response.status_code == 200
        assert response.data['concept_id'] == 6122008

        response = self.client.get('/terminology/description/2884452019/?active=false')
        assert response.status_code == 404

    def test_single_description_inactive(self):
        response = self.client.get('/terminology/description/725272017/?active=false')
        assert response.status_code == 200
        assert response.data['term'] == 'Quinidine bisulfate 250mg m/r tablet (substance)'

    def test_description_list_by_concept_id(self):
        response = self.client.get('/terminology/descriptions/concept_id/374978005/')
        assert response.status_code == 200
        assert response.data['results'][0]['term'] == 'Procainamide hydrochloride 250mg tablet (product)'  # noqa


class TestReferenceSets(APITestCase):
    def test_language_reference_sets(self):
        response = self.client.get('/terminology/refset/language/')
        assert response.status_code == 200
        assert response.data['results'][0]['id'] == '80000517-8513-5ca0-a44c-dc66f3c3a1c6'

    def test_language_reference_sets_module(self):
        response = self.client.get('/terminology/refset/language/900000000000207008/')
        assert response.status_code == 200
        assert response.data['results'][0]['id'] == '80000517-8513-5ca0-a44c-dc66f3c3a1c6'

    def test_language_reference_set_detail(self):
        response = self.client.get(
            '/terminology/refset/detail/language/80000517-8513-5ca0-a44c-dc66f3c3a1c6/')
        assert response.status_code == 200
        assert response.data['id'] == '80000517-8513-5ca0-a44c-dc66f3c3a1c6'

    def test_language_reference_sets_search(self):
        response = self.client.get('/terminology/refset/language/?search=United States of America')
        assert response.status_code == 200
        assert response.data['results'][0]['id'] == '80000755-c5d9-5bd8-bb64-ab8236d240d7'

    def test_association_reference_sets(self):
        response = self.client.get('/terminology/refset/association/')
        assert response.status_code == 200
        assert response.data['results'][0]['id'] == '80001d7e-b1b9-56ac-9768-308cabe31117'

    def test_association_reference_sets_module(self):
        response = self.client.get('/terminology/refset/association/900000000000207008/')
        assert response.status_code == 200
        assert response.data['results'][0]['id'] == '80001d7e-b1b9-56ac-9768-308cabe31117'

    def test_association_reference_set_detail(self):
        response = self.client.get(
            '/terminology/refset/detail/association/80001d7e-b1b9-56ac-9768-308cabe31117/')
        assert response.status_code == 200
        assert response.data['id'] == '80001d7e-b1b9-56ac-9768-308cabe31117'

    def test_association_reference_sets_search(self):
        response = self.client.get('/terminology/refset/association/?search=possibly equivalent to')
        assert response.status_code == 200
        assert response.data['results'][0]['id'] == '8001aeda-719f-5d07-a4aa-00b734b748da'

    def test_attribute_value_reference_sets(self):
        response = self.client.get('/terminology/refset/attribute_value/')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'Description inactivation indicator reference set'  # noqa

    def test_attribute_value_reference_sets_module(self):
        response = self.client.get('/terminology/refset/attribute_value/900000000000207008/')
        assert response.status_code == 200
        assert len(response.data['results']) == 0

    def test_attribute_value_reference_set_detail(self):
        response = self.client.get(
            '/terminology/refset/detail/attribute_value/6c51a6b7-4adc-5cad-9b3c-e8a35f59aca4/')
        assert response.status_code == 200
        assert response.data['id'] == '6c51a6b7-4adc-5cad-9b3c-e8a35f59aca4'

    def test_attribute_value_reference_sets_search(self):
        response = self.client.get(
            '/terminology/refset/attribute_value/?search=description inactivation')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'Description inactivation indicator reference set'  # noqa

    def test_complex_map_reference_sets(self):
        response = self.client.get('/terminology/refset/complex_map/')
        assert response.status_code == 200
        assert response.data['results'][-1]['refset_name'] == 'ICD-9-CM equivalence complex map reference set'  # noqa

    def test_complex_map_reference_sets_module(self):
        response = self.client.get('/terminology/refset/complex_map/900000000000207008/')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'ICD-9-CM equivalence complex map reference set'  # noqa

    def test_complex_map_reference_set_detail(self):
        response = self.client.get(
            '/terminology/refset/detail/complex_map/8001c330-04d7-5940-a329-bbe09d6137b1/')
        assert response.status_code == 200
        assert response.data['id'] == '8001c330-04d7-5940-a329-bbe09d6137b1'

    def test_complex_map_reference_sets_search(self):
        response = self.client.get('/terminology/refset/complex_map/?search=ICD-9-CM equivalence')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'ICD-9-CM equivalence complex map reference set'  # noqa

    def test_simple_reference_sets(self):
        response = self.client.get('/terminology/refset/simple/')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'Manufactured material simple reference set'  # noqa

    def test_simple_reference_sets_module(self):
        response = self.client.get('/terminology/refset/simple/900000000000207008/')
        assert response.status_code == 200
        assert len(response.data['results']) == 0

    def test_simple_reference_set_detail(self):
        response = self.client.get(
            '/terminology/refset/detail/simple/f60c9ef2-fdfd-5fae-afd5-34aca8872cc5/')
        assert response.status_code == 200
        assert response.data['id'] == 'f60c9ef2-fdfd-5fae-afd5-34aca8872cc5'

    def test_simple_reference_sets_search(self):
        response = self.client.get('/terminology/refset/simple/?search=manufactured material')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'Manufactured material simple reference set'  # noqa

    def test_ordered_reference_sets(self):
        response = self.client.get('/terminology/refset/ordered/')
        assert response.status_code == 200
        assert len(response.data['results']) == 0

    def test_ordered_reference_sets_module(self):
        response = self.client.get('/terminology/refset/ordered/900000000000207008/')
        assert response.status_code == 200
        assert len(response.data['results']) == 0

    def test_ordered_reference_sets_search(self):
        response = self.client.get('/terminology/refset/ordered/?search=manufactured material')
        assert response.status_code == 200
        assert len(response.data['results']) == 0

    def test_simple_map_reference_sets(self):
        response = self.client.get('/terminology/refset/simple_map/')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'SNOMED RT ID simple map'

    def test_simple_map_reference_sets_module(self):
        response = self.client.get('/terminology/refset/simple_map/900000000000207008/')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'SNOMED RT ID simple map'

    def test_simple_map_reference_set_detail(self):
        response = self.client.get(
            '/terminology/refset/detail/simple_map/80001267-7451-550a-82f0-92cc3bdfe890/')
        assert response.status_code == 200
        assert response.data['id'] == '80001267-7451-550a-82f0-92cc3bdfe890'

    def test_simple_map_reference_sets_search(self):
        response = self.client.get('/terminology/refset/simple_map/?search=ctv3 simple map')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'CTV3 simple map'

    def test_query_specification_reference_sets(self):
        response = self.client.get('/terminology/refset/query_specification/')
        assert response.status_code == 200
        assert len(response.data['results']) == 0

    def test_query_specification_reference_sets_module(self):
        response = self.client.get('/terminology/refset/query_specification/900000000000207008/')
        assert response.status_code == 200
        assert len(response.data['results']) == 0

    def test_module_dependency_reference_sets(self):
        response = self.client.get('/terminology/refset/module_dependency/')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'Module dependency'

    def test_module_dependency_reference_sets_module(self):
        response = self.client.get('/terminology/refset/module_dependency/900000000000207008/')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'Module dependency'

    def test_module_dependency_reference_set_detail(self):
        response = self.client.get(
            '/terminology/refset/detail/module_dependency/f6431457-161b-5b46-9217-573c20c00070/')
        assert response.status_code == 200
        assert response.data['id'] == 'f6431457-161b-5b46-9217-573c20c00070'

    def test_module_dependency_reference_sets_search(self):
        response = self.client.get(
            '/terminology/refset/module_dependency/?search=Module dependency')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'Module dependency'

    def test_reference_set_descriptor_reference_sets(self):
        response = self.client.get('/terminology/refset/reference_set_descriptor/')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'Reference set descriptor'

    def test_reference_set_descriptor_reference_sets_module(self):
        response = self.client.get(
            '/terminology/refset/reference_set_descriptor/900000000000207008/')
        assert response.status_code == 200
        assert len(response.data['results']) == 0

    def test_reference_set_descriptor_reference_set_detail(self):
        response = self.client.get(
            '/terminology/refset/detail/reference_set_descriptor/daf36341-bc20-2770-e044-0003ba13161a/')  # noqa
        assert response.status_code == 200
        assert response.data['id'] == 'daf36341-bc20-2770-e044-0003ba13161a'

    def test_extended_map_reference_sets(self):
        response = self.client.get('/terminology/refset/extended_map/')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'ICD-10 complex map reference set (foundation metadata concept)'  # noqa

    def test_extended_map_reference_sets_module(self):
        response = self.client.get('/terminology/refset/extended_map/900000000000207008/')
        assert response.status_code == 200
        assert len(response.data['results']) == 0

    def test_extended_map_reference_set_detail(self):
        response = self.client.get(
            '/terminology/refset/detail/extended_map/80005aeb-477c-53dc-9a5c-ce723ca264cb/')
        assert response.status_code == 200
        assert response.data['id'] == '80005aeb-477c-53dc-9a5c-ce723ca264cb'

    def test_extended_map_reference_sets_search(self):
        response = self.client.get('/terminology/refset/extended_map/?search=ICD-10 complex map')
        assert response.status_code == 200
        assert response.data['results'][0]['refset_name'] == 'ICD-10 complex map reference set (foundation metadata concept)'  # noqa

    def test_annotation_reference_sets(self):
        response = self.client.get('/terminology/refset/annotation/')
        assert response.status_code == 200
        assert len(response.data['results']) == 0

    def test_description_format_reference_sets(self):
        response = self.client.get('/terminology/refset/description_format/')
        assert response.status_code == 200
        assert response.data['results'][0]['referenced_component_name'] == 'Fully specified name'

    def test_description_format_reference_sets_module(self):
        response = self.client.get('/terminology/refset/description_format/900000000000207008/')
        assert response.status_code == 200
        assert response.data['results'][0]['referenced_component_name'] == 'Fully specified name'

    def test_description_format_reference_set_detail(self):
        response = self.client.get(
            '/terminology/refset/detail/description_format/807f775b-1d66-5069-b58e-a37ace985dcf/')
        assert response.status_code == 200
        assert response.data['id'] == '807f775b-1d66-5069-b58e-a37ace985dcf'


class TestFilters(APITestCase):
    def test_fields_concept_filter(self):
        response = self.client.get('/terminology/concepts/?fields=id,preferred_term')
        assert response.status_code == 200
        assert response.data['results'][0].get('fully_specified_name', None) is None

    def test_concept_json_filter(self):
        response = self.client.get('/terminology/concepts/?parents=10363901000001102,10363701000001104&search=150mg capsules')  # noqa
        assert response.status_code == 200
        assert response.data['results'][0].get('fully_specified_name') == 'Disopyramide 150mg capsules (A A H Pharmaceuticals Ltd) (product)'  # noqa

        response = self.client.get('/terminology/concepts/?ancestors=10363901000001102,10363701000001104&search=150mg capsules')  # noqa
        assert response.status_code == 200
        assert response.data['results'][0].get('fully_specified_name') == 'Disopyramide 150mg capsule (substance)'  # noqa

        response = self.client.get('/terminology/concepts/?descendants=11959009')
        assert response.status_code == 200
        assert response.data['results'][0].get('fully_specified_name') == 'Class Ia antiarrhythmic drug (product)'  # noqa

        response = self.client.get('/terminology/concepts/?parents=10363901000001102,foobar')  # noqa
        assert response.status_code == 500
        assert 'detail' in response.data

        response = self.client.get('/terminology/concepts/?children=10363901000001102,10363701000001104')  # noqa
        assert response.status_code == 200
        assert len(response.data['results']) == 0

        response = self.client.get('/terminology/concepts/?children=10363901000001102,foobar')  # noqa
        assert response.status_code == 500
        assert 'detail' in response.data

        refset_id = 900000000000497000
        response = self.client.get('/terminology/concepts/?member_of={}'.format(refset_id))
        first_result = response.data['results'][0]['id']
        concept = Concept.objects.get(id=int(first_result))
        assert refset_id in [refset['refset_id']
                             for refset in concept.reference_set_memberships]

    def test_page_size_concept_filter(self):
        response = self.client.get('/terminology/concepts/?fields=id,preferred_term&page_size=20')
        assert response.status_code == 200
        assert len(response.data['results']) == 20
        assert response.data['results'][0].get('fully_specified_name', None) is None

        response = self.client.get('/terminology/concepts/?fields=id,preferred_term&page_size=0')
        assert response.status_code == 500
        assert 'detail' in response.data.keys()

    def test_fields_single_concept_filter(self):
        response = self.client.get('/terminology/concept/6122008/?fields=id,preferred_term')
        assert response.status_code == 200
        assert response.data.get('fully_specified_name', None) is None

    def test_fields_single_concept_empty_param_filter(self):
        response = self.client.get('/terminology/concept/6122008/?fields=''')
        assert response.status_code == 200
        assert response.data.get('fully_specified_name', None) is not None

    def test_fields_single_description_empty_params_filter(self):
        response = self.client.get(
            '/terminology/description/56988101000001116/?fields='''
        )
        assert response.status_code == 200
        assert response.data.get('term', None) is not None

    def test_full_concept_filter(self):
        response = self.client.get('/terminology/concepts/?full=true')

        assert response.status_code == 200
        assert len(response.data['results'][1].get(
            'reference_set_memberships',
            None)) >= 1

    def test_full_description_filter(self):
        response = self.client.get('/terminology/descriptions/?full=true')
        assert response.status_code == 200
        assert len(response.data['results'][0].get(
            'reference_set_memberships',
            None)) == 0

    def test_fields_description_filter(self):
        response = self.client.get('/terminology/descriptions/?fields=reference_set_memberships')
        assert response.status_code == 200
        assert len(response.data['results'][0].get(
            'reference_set_memberships',
            None)) == 0

    def test_fields_single_description_filter(self):
        response = self.client.get(
            '/terminology/description/220309016/?fields=effective_time,term')
        assert response.status_code == 200
        assert response.data['effective_time'] == '2003-07-31'

    def test_exclude_fields_concept_filter(self):
        response = self.client.get(
            '/terminology/concepts/?fields=id,preferred_term&exclude_fields=true'
        )
        assert response.status_code == 200
        assert response.data['results'][0].get('preferred_term', None) is None

    def test_strip_fields_refset_filter(self):
        response = self.client.get('/terminology/refset/language/?fields=id,module_id')
        assert response.status_code == 200
        assert response.data['results'][0].get('refset_name', None) is None

    def test_strip_fields_refset_filter_excluding_fields(self):
        response = self.client.get(
            '/terminology/refset/language/?fields=id,module_id&exclude_fields=true')
        assert response.status_code == 200
        assert response.data['results'][0].get('module_id', None) is None


class TestAPI(APITestCase):
    def test_api_root(self):
        response = self.client.get('/')
        assert response.status_code == 200
        assert type(response.data) == OrderedDict
        assert response.data['current_release_information'] == 'http://testserver/terminology/version/current/'  # noqa

    def test_deterministic_order_of_api_root_urls(self):
        response = self.client.get('/')
        assert response.status_code == 200
        second_item = next(islice(response.data.items(), 2, None))
        concepts = ('all_concepts', 'http://testserver/terminology/concepts/')
        assert second_item == concepts

    def test_current_release(self):
        response = self.client.get('/terminology/version/current/')
        assert response.status_code == 200
        assert response.data['release_date'] == '2016-01-31'

        factory = APIRequestFactory()
        request = factory.get('/terminology/version/current/')
        response = current_release_information(Request(request))
        assert response.data['release_date'] == '2016-01-31'

    def test_historical_releases(self):
        response = self.client.get('/terminology/versions/')
        assert response.status_code == 200
        assert response.data[0]['release_date'] == '2016-01-31'

        factory = APIRequestFactory()
        request = factory.get('/terminology/version/current/')
        response = historical_release_information(Request(request))
        assert response.data[1]['release_date'] == '2015-07-31'

    def test_active_concepts_filter(self):
        view = ListConcepts.as_view()
        factory = APIRequestFactory()
        request = factory.get('/terminology/concepts/?active=true')
        response = view(request)
        assert '108003' in response.data['results'][0]['url']

    def test_inactive_concept_filter(self):
        view = ListConcepts.as_view()
        factory = APIRequestFactory()
        request = factory.get('/terminology/concepts/?active=false')
        response = view(request)
        assert len(response.data['results']) == 0

    def test_incorrect_release_date_filter(self):
        view = ListConcepts.as_view()
        factory = APIRequestFactory()
        request = factory.get('/terminology/concepts/?release_date=2016-01-fdfdofa')
        response = view(request)
        assert response.data['detail'] == "time data '2016-01-fdfdofa' does not match format '%Y-%m-%d'"  # noqa

    def test_correct_release_date_filter(self):
        view = ListConcepts.as_view()
        factory = APIRequestFactory()
        request = factory.get('/terminology/concepts/?release_date=2016-01-31')
        response = view(request)
        assert response.data['results'][0]['effective_time'] == '2016-01-31'

    def test_evaluation_release_status(self):
        view = ListConcepts.as_view()
        factory = APIRequestFactory()
        request = factory.get('/terminology/concepts/?release_status=E')
        response = view(request)
        assert 'detail' in response.data.keys()

    def test_developmental_release_status(self):
        view = ListConcepts.as_view()
        factory = APIRequestFactory()
        request = factory.get('/terminology/concepts/?release_status=D')
        response = view(request)
        assert 'detail' in response.data.keys()

    def test_concept_detail_serializer(self):
        concept_id = 6122008
        response = self.client.get(
            '/terminology/concept/{}/?fields=reference_set_memberships'.format(concept_id))

        assert 'reference_set_memberships' in response.data.keys()


class DataLoadTests(TestCase):
    def test_concept(self):
        concept = Concept.objects.get(id=6122008)
        self.assertEqual(concept.definition_status_id, 900000000000073002)

    def test_description(self):
        descriptions = Description.objects.filter(concept_id=374978005)
        self.assertEqual(descriptions[0].term, "Procainamide hydrochloride 250mg tablet (product)")


class TestSearch(TestCase):
    def test_concept_search_filter(self):
        concepts = Concept.objects.filter(descriptions__tsv_search='quinidine')
        assert concepts[0].__str__() == '| Quinidine (substance) | 31306009'

    def test_refset_search_filter(self):
        refsets = LanguageReferenceSetDenormalizedView.objects.filter(
            refset_name__xsearch='United').filter(
                refset_name__xsearch='States').filter(
                    refset_name__xsearch='America')

        assert refsets[0].refset_name == 'United States of America English language reference set (foundation metadata concept)'  # noqa

    def test_isearch_filter(self):
        class TestSearchView(ListAPIView):
            queryset = Description.objects.all()
            serializer_class = DescriptionListSerializer
            filter_backends = (OrderingFilter, CommonSearchFilter)
            search_fields = ('term',)
            ordering = ('id',)

        view = TestSearchView.as_view()
        factory = APIRequestFactory()
        request = factory.get('/terminology/descriptions/?search=antiarrythmic drug')
        response = view(request)

        assert response.status_code == 200
        descriptions = Description.objects.filter(
            term__isearch='antiarrhythmic').filter(term__isearch='drug')
        assert descriptions[0].term == 'Class Ia antiarrhythmic drug (product)'
