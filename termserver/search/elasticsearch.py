__author__ = 'ngurenyaga'
"""Set up ElasticSearch indexing and search"""
from core.models import ConceptView
from elasticutils.contrib.django import MappingType, Indexable
from elasticutils.contrib.django.tasks import index_objects
from django.core.exceptions import MultipleObjectsReturned


class ConceptMappingType(MappingType, Indexable):
    """Concepts are the primary searchable item"""

    @classmethod
    def get_index(cls):
        """Explicitly set the index name, so that we can add other index types in future with minimal disruption"""
        return 'concept-index'

    @classmethod
    def get_mapping_type_name(cls):
        """Name of the concept type in the search index"""
        return 'concept'

    @classmethod
    def get_model(cls):
        """The mapping will use the materialized view"""
        return ConceptView

    def get_object(self):
        """Overridden because the primary key field is concept_id, not id"""
        return self.get_model()._get(concept_id=self._id)

    @classmethod
    def get_mapping(cls):
        """Create an ElasticSearch mapping for Concept search

        A deliberate choice has been made to index only the information that is relevant to search.
        The rest of the information will always be a single ( fast ) SQL query away.

        We rely upon the fact the ElasticSearch transparently indexes lists - the reason why there is no "special
        treatment" for "descriptions".

        The "preferred_term" and "fully_specified_name" are stored in the index - because they are commonly used in
        rendering, and it is beneficial to be able to render them without an additional database query.

        The "parents" and "children" fields concern themselves only with the subsumption ( "is a" ) relationship. This
        is by far the most frequently interrogated relationship.
        """
        return {
            'properties': {
                # Unique identifier, to be used to look up the concept when more detail is needed
                # It is stored but not analyzed
                'concept_id': {
                    'type': 'long',
                    'index': 'no',  # Not searchable; because SCTIDs are not meaningful
                    'coerce': False  # We are strict
                },
                # The next group of properties will be used for filtering
                # They are stored but not analyzed
                'active': {
                    'type': 'boolean',
                    'index': 'no'  # Indexing boolean fields is close to useless
                },
                'is_primitive': {
                    'type': 'boolean',
                    'index': 'no'
                },
                'module_id': {
                    'type': 'long',
                    'index': 'no',
                    'coerce': False
                },
                'module_name': {
                    'type': 'string',
                    'index': 'analyzed',
                    'analyzer': 'standard',
                    'index_analyzer': 'standard',
                    'search_analyzer': 'standard'
                },
                # The primary "human identifiers" of a concept; stored but not analyzed
                'fully_specified_name': {
                    'type': 'string',
                    'index': 'analyzed',
                    'analyzer': 'standard',
                    'index_analyzer': 'standard',
                    'search_analyzer': 'standard'
                },
                'preferred_term': {
                    'type': 'string',
                    'index': 'analyzed',
                    'analyzer': 'standard',
                    'index_analyzer': 'standard',
                    'search_analyzer': 'standard'
                },
                # Indexed string ( array ) fields
                # These fields are analyzed ( searchable ); the default search field should be "descriptions"
                'descriptions': {
                    'type': 'string',
                    'index': 'analyzed',
                    'analyzer': 'standard',
                    'index_analyzer': 'standard',
                    'search_analyzer': 'standard'
                },
                # Relationship fields - used solely for filtering; only the target concept_ids are stored
                # Stored but not analyzed
                'parents': {
                    'type': 'long',
                    'index': 'no',
                    'coerce': False
                },
                'children': {
                    'type': 'long',
                    'index': 'no',
                    'coerce': False
                }
            }
        }

    @classmethod
    def extract_document(cls, obj_id, obj=None):
        """Convert the model instance into a searchable document"""
        if obj is None:
            try:
                obj = cls.get_model().objects.get(concept_id=obj_id)
            except MultipleObjectsReturned:
                obj = cls.get_model().objects.filter(concept_id=obj_id)[0]

        return {
            'id': obj.id,
            'concept_id': obj.concept_id,
            'active': obj.active,
            'is_primitive': obj.is_primitive,
            'module_id': obj.module_id,
            'module_name': obj.module_name,
            'fully_specified_name': obj.fully_specified_name,
            'preferred_term': obj.preferred_term,
            'descriptions': list(set([item["term"] for item in obj.descriptions_list])),
            'parents': list(set([rel["concept_id"] for rel in obj.is_a_parents])),
            'children': list(set([rel["concept_id"] for rel in obj.is_a_children]))
        }


def search():
    searcher = ConceptMappingType.search()


def bulk_index():
    """Criminally ugly code ensues

    And I'm too bloody lazy to "do the right thing". Maybe you aren't.
    """
    model_ids = list(ConceptMappingType.get_model().objects.all().values_list('id', flat=True))
    index_objects(ConceptMappingType, model_ids, 1000)

# TODO For tests, use from elasticutils.contrib.django.estestcase import ESTestCase and default ES_DISABLED to True, turning it on selectively when needed
# TODO Use a unique index name for tests, so that tests do not clobber the production database
# TODO When settings.DEBUG = True, call django.db.reset_queries() occasionally; Django "helpfully" caches all queries

# TODO Synonyms - process SNOMED word equivalents into synonyms
# TODO Create custom analyzer for synonyms and set it up as the query time analyzer
# TODO Ensure that all queries have pagination - with 25 items as our default
# TODO "full" queries: use a **common terms query** with the "and" operator for low frequency and "or" operator for high frequency; index analyzer to standard
# TODO Add autocomplete field to mapping; edge-ngram, 3-20 characters
# TODO Add query template, with support for filtering by parents, children, module, primitive, active
# TODO Ensure that synonym support can be turned on/off via query parameter
# TODO Incorporate phrase suggester into all searches
# TODO Incorporate "more like this" into all searches; easy - see below; pass it the search object
    # s = S().filter(product='firefox')
    # mlt = MLT(2034, s=s)

# TODO Create a single "fab build" step that does everything up to indexing
# TODO Create a "fab backup" step that works with Google Object storage
# TODO Create a docker container build process; be sure to start Celery too
# TODO Fix process around downloading, preparing and updating UK release content
# TODO Implement API and perform sanity checks on concepts using UMLS UTS search engine
# TODO Implement search
# TODO Implement pep8 checks in tests
# TODO Fix test coverage issues
# TODO Use the celery task to index individual concepts whenever something changes? What about the precomputation?
