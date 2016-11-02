import operator
from functools import reduce
from django.db import models
from rest_framework.exceptions import APIException
from rest_framework_extensions.mixins import ReadOnlyCacheResponseAndETAGMixin
from rest_framework.filters import BaseFilterBackend, OrderingFilter
from .utils import (parse_date_param,
                    as_bool,
                    UNIMPLEMENTED_RELEASE_STATUS_ERROR,
                    ModifiablePageSizePagination)

from .caching import (ListAPIKeyConstructor,
                      RetrieveAPIKeyConstructor)


class SearchOrderingFilter(OrderingFilter):
    def get_ordering(self, request, queryset, view):
        # No ordering was included, or all the ordering fields were invalid
        params = request.query_params

        if 'search' in params.keys() and params.get('search', None):
            return ('-rank',)
        else:
            return self.get_default_ordering(view)


@models.Field.register_lookup
class JSONArrayLookup(models.Lookup):
    """A Lookup that checks if a particular relation is satisfied inside a
    JSON array. E.g. if descriptions=[{'id': 1,'term':'desc_1'},{'id':
    2,'term':'desc_2'}] contains 'id':1.

    """
    lookup_name = 'array_contains_id'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)

        object_field = rhs_params[0].adapted[0]

        assert object_field in ('concept_id', 'refset_id')

        component_id = rhs_params[0].adapted[1]

        query = "get_ids_from_jsonb(%s, '{}')".format(object_field) % lhs

        return query + " @> ARRAY[%s::bigint]" % rhs, [component_id]


class JSONFieldFilter(BaseFilterBackend):
    """This filter enables a client to query the concept list endpoint with
the params: ?parents= and ?children=, which take a comma-separated list
of valid sctids and return the concepts in the hierarchy
selected. ?parents= selects concepts whose parents are in the list of
sctids, while ?children= selects concepts whose children are in the
sctid list.

    """
    def get_json_field_queries(self, component_id_list, json_field_name, object_field):
        queries = []
        for component_id in component_id_list.split(','):
            try:
                component_id = int(component_id)
            except ValueError as e:
                raise APIException(detail="'{}' is not an integer. {}".format(component_id, e))
            queries.append(models.Q(**{'{}__array_contains_id'.format(json_field_name):
                                       (object_field, component_id)}))
        return queries

    def filter_queryset(self, request, queryset, view):
        parents = request.query_params.get('parents', None)
        children = request.query_params.get('children', None)

        ancestors = request.query_params.get('ancestors', None)
        descendants = request.query_params.get('descendants', None)

        refset_id = request.query_params.get('member_of', None)

        if parents:
            queries = self.get_json_field_queries(parents, 'parents', 'concept_id')
            queryset = queryset.filter(reduce(operator.or_, queries))

        if children:
            queries = self.get_json_field_queries(children, 'children', 'concept_id')
            queryset = queryset.filter(reduce(operator.or_, queries))

        if ancestors:
            queries = self.get_json_field_queries(ancestors, 'ancestors', 'concept_id')
            queryset = queryset.filter(reduce(operator.or_, queries))

        if descendants:
            queries = self.get_json_field_queries(descendants, 'descendants', 'concept_id')
            queryset = queryset.filter(reduce(operator.or_, queries))

        if refset_id:
            queries = self.get_json_field_queries(refset_id, 'reference_set_memberships',
                                                  'refset_id')
            queryset = queryset.filter(reduce(operator.or_, queries))

        return queryset


class GlobalFilterMixin(ReadOnlyCacheResponseAndETAGMixin):
    """This mixin supports filtering by release_date, release_status,
page_size, and the 'active' value in any component, globally. Any view
that uses this mixin will have the filters described here.

+ `release_status` will, for now, return all components as 'R' for
Release, since we're using SNOMED CT data from the UK release
center. When we start creating our own content, we'll have two new
release statuses 'Evaluation' and 'Development'.

+ `release_date` will filter by the effective_time field, which is present
in all components. Should be useful to restrict the active subset of
SNOMED CT to components that were released on that day.

+ `active` enables us to get only active or inactive components. It is
important to remember that SNOMED is a log-structured dataset. Nothing
is ever deleted, but updated with a new effective time and value of
'active', which is boolean.

+ the pagination_class is set to ModifiablePageSizePagination because
this allows us to set the page_size param to something that fits the
size of the view being used.

    """

    pagination_class = ModifiablePageSizePagination

    object_etag_func = RetrieveAPIKeyConstructor()
    object_cache_key_func = RetrieveAPIKeyConstructor()

    list_etag_func = ListAPIKeyConstructor()
    list_cache_key_func = ListAPIKeyConstructor()

    def get_queryset(self):
        queryset = super(GlobalFilterMixin, self).get_queryset()
        release_date = self.request.query_params.get('release_date', None)
        release_status = self.request.query_params.get('release_status', 'R')
        active = self.request.query_params.get('active', True)

        if release_status == 'R':
            queryset = queryset.filter(active=as_bool(active))

            if release_date:
                try:
                    parsed_date = parse_date_param(release_date, from_filter=True)
                    queryset = queryset.filter(effective_time=parsed_date)
                except ValueError as error:
                    raise APIException(detail=error)

        elif release_status == 'E' or release_status == 'D':  # pragma: no cover
            raise APIException(detail=UNIMPLEMENTED_RELEASE_STATUS_ERROR)

        return queryset
