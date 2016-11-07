import operator
from functools import reduce
from rest_framework.filters import SearchFilter
from django.db import models
from django.utils import six
from stop_words import get_stop_words
from .utils import execute_query
from django.contrib.postgres.search import (SearchQuery,
                                            SearchVectorField,
                                            SearchVectorExact)
from django.db.models.expressions import Func


class WordEquivalentMixin(object):
    def construct_tsquery_param(self, words):
        """Takes a list of words and returns a to_tsquery parameter."""
        query = ')|('.join([' & '.join(['{}:*'.format(w)
                                        for w in reversed(word.split())])
                            for word in words])
        return '(' + query + ')'

    def get_word_equivalents(self, word):
        """Gets a word and returns a list of equivalent words formatted as a
to_tsquery parameter.

        """
        equivalent_words = execute_query("select get_word_equivalents(%s)", word)
        if equivalent_words:
            equivalent_words.append(word)
            return equivalent_words
        else:
            return [word]


class JSONSearchVector(Func):
    function = 'get_tsvector_from_json'

    _output_field = SearchVectorField()

    def as_sql(self, compiler, connection, function=None, template=None):
        template = "%(function)s(%(expressions)s)"
        sql, params = super(JSONSearchVector,
                            self).as_sql(compiler,
                                         connection,
                                         function=function,
                                         template=template)
        return sql, params


class PrefixMatchSearchQuery(SearchQuery, WordEquivalentMixin):
    def as_sql(self, compiler, connection):
        if self.value:  # pragma: no branch
            params = self.construct_tsquery_param(self.value)
        template = 'to_tsquery(%s)'
        return template, [params]


@models.Field.register_lookup
class TSVJSONSearch(SearchVectorExact, WordEquivalentMixin):
    """This lookup constructs a string matching the to_tsquery format from
an input string, enabling word-equivalence checking and prefix matching
during search.

This lookup also performs a call to a stored procedure in
'migrations/sql/text_search_pipeline.sql', called 'get_tsvector_from_json'. It
takes data from a json array field, extracts the 'term' field from each
json object inside it, concatenates the strings and returns the tsvector
representation of the concatenated string. This way, we can perform a
full-text search on all the descriptions of a concept. The same function
is called to create an index on the 'descriptions' field of the Concept
model.

    """
    lookup_name = 'json_search'

    def process_lhs(self, qn, connection):
        if not isinstance(self.lhs.output_field, SearchVectorField):  # pragma: no branch
            self.lhs = JSONSearchVector(self.lhs)
        lhs, lhs_params = super(TSVJSONSearch, self).process_lhs(qn, connection)
        return lhs, lhs_params

    def process_rhs(self, qn, connection):
        rhs, rhs_params = super(TSVJSONSearch, self).process_rhs(qn, connection)

        return rhs, rhs_params


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


class RefsetSearchFilter(SearchFilter):
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

        # only be forgiving for terms longer than 5 characters.
        long_search_terms = [execute_query("select correct(%s)", word)
                             for word in terms
                             if word not in english_stop_words
                             and len(word) > 5]

        short_search_terms = [word for word in terms
                              if word not in english_stop_words
                              and len(word) <= 5]

        return long_search_terms + short_search_terms

    def construct_search(self, field_name):
        return "%s__xsearch" % field_name[1:]

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
