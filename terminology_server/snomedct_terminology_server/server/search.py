import operator
from functools import reduce
from rest_framework.filters import SearchFilter
from django.db import models
from django.utils import six
from stop_words import get_stop_words
from .utils import execute_query


@models.Field.register_lookup
class TSVJSONSearch(models.Lookup):
    """This lookup performs a call to a stored procedure in
'migrations/sql/final_load.sql', called 'get_tsvector_from_json'. It
takes data from a json array field, extracts the 'term' field from each
json object inside it, concatenates the strings and returns the tsvector
representation of the concatenated string. This way, we can perform a
full-text search on all the descriptions of a concept. The same function
is called to create an index on the 'descriptions' field of the Concept
model.
    """
    lookup_name = 'tsv_search'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)

        # Clean up rhs_params since it assumes the type of model field
        # it's searching on: JSON in the case of descriptions in a
        # concept
        rhs_params = [str(rhs_params[0])[2:-2]]
        params = lhs_params + rhs_params

        return 'get_tsvector_from_json(%s) @@ to_tsquery(%s)' % (lhs, rhs), params


@models.Field.register_lookup
class RefsetSearch(models.Lookup):
    """Performs a tsvector search on a stemmed term from the 'refset_name'
field from any of the reference set models. plainto_tsquery converts any
string into a tsquery, i.e. a stemmed version of the string
    """
    lookup_name = 'xsearch'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return 'to_tsvector(%s) @@ to_tsquery(%s)' % (lhs, rhs), params


@models.Field.register_lookup
class Search(models.Lookup):
    """Provides trigram similarity search on any model that isn't a concept
or a reference set. Currently unused."""
    lookup_name = 'isearch'

    def as_sql(self, compiler, connection):

        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return 'to_tsvector(%s) @@ to_tsquery(%s)' % (lhs, rhs), params


class CommonSearchFilter(SearchFilter):
    """This is a search filter with an analysis pipeline that includes
stopword removal, and autocorrection of input terms using the
'correct(text)' stored procedure.
    """
    # The URL query parameter used for the search.
    search_param = 'search'

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, '')

        english_stop_words = get_stop_words('en')

        terms = params.replace(',', ' ').split()

        search_terms = [execute_query("select correct(%s)", word)
                        for word in terms
                        if word not in english_stop_words]

        return search_terms

    def construct_search(self, field_name):
        if field_name.startswith('@'):
            return "%s__tsv_search" % field_name[1:]
        elif field_name.startswith('%'):
            return "%s__xsearch" % field_name[1:]
        else:
            return "%s__isearch" % field_name

    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'search_fields', None)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:  # pragma: no branch
            return queryset

        orm_lookups = [
            self.construct_search(six.text_type(search_field))
            for search_field in search_fields
        ]

        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            queryset = queryset.filter(reduce(operator.and_, queries))
        return queryset


class RefsetSearchFilter(CommonSearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'search_fields', None)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:  # pragma: no branch
            return queryset

        orm_lookups = [
            self.construct_search(six.text_type(search_field))
            for search_field in search_fields
        ]

        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            queryset = queryset.filter(reduce(operator.or_, queries))
        return queryset
