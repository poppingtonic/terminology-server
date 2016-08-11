import operator
from functools import reduce

from rest_framework.filters import SearchFilter
from django.db import models
from django.db.models import query
from django.utils import six

from stop_words import get_stop_words

@models.Field.register_lookup
class TSVJSONSearch(models.Lookup):
    lookup_name = 'tsv_search'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)

        if type(rhs_params) == list and rhs_params[0].__class__.__name__ == 'Json': # pragma: no branch
            rhs_params = [str(rhs_params[0])[2:-2]]

        params = lhs_params + rhs_params
        return 'get_tsvector_from_json(%s) @@ plainto_tsquery(%s)' % (lhs, rhs), params

@models.Field.register_lookup
class RefsetSearch(models.Lookup):
    lookup_name = 'xsearch'

    def as_sql(self, compiler, connection):
        similarity__gt = 0.2
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return 'to_tsvector(%s) @@ plainto_tsquery(%s)' % (lhs, rhs), params


@models.Field.register_lookup
class Search(models.Lookup):
    lookup_name = 'isearch'

    def as_sql(self, compiler, connection):
        similarity__gt = 0.2
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return 'SIMILARITY(%s, %s)>%s' % (lhs, rhs, similarity__gt), params


class CommonSearchFilter(SearchFilter):
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

        search_terms = [word for word in terms
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

        if not search_fields or not search_terms: # pragma: no branch
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
