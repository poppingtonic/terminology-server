from .api_tests import *
from .unit_tests import *

from django_webtest import WebTest
import json

class ConceptWebTestCase(WebTest):
    def test_list(self):
        concept_list = self.app.get('/terminology/concepts/')
        concept_list.charset = 'utf-8'
        response_data = json.loads(concept_list.text)['results']
        assert response_data[0]['id'] == 6122008
