import operator
from functools import reduce
from django.db import models
from rest_framework.exceptions import APIException
from rest_framework_extensions.mixins import ReadOnlyCacheResponseAndETAGMixin
from rest_framework.filters import BaseFilterBackend, OrderingFilter
from .utils import (parse_date_param,
                    as_bool,
                    UNIMPLEMENTED_RELEASE_STATUS_ERROR,
                    ModifiablePageSizePagination,
                    get_json_field_queries)

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

    def filter_queryset(self, request, queryset, view):
        parents = request.query_params.get('parents', None)
        children = request.query_params.get('children', None)

        ancestors = request.query_params.get('ancestors', None)
        descendants = request.query_params.get('descendants', None)

        refset_id = request.query_params.get('member_of', None)

        if parents:
            queries = get_json_field_queries(parents, 'parents', 'concept_id')
            queryset = queryset.filter(reduce(operator.or_, queries))

        if children:
            queries = get_json_field_queries(children, 'children', 'concept_id')
            queryset = queryset.filter(reduce(operator.or_, queries))

        if ancestors:
            queries = get_json_field_queries(ancestors, 'ancestors', 'concept_id')
            queryset = queryset.filter(reduce(operator.or_, queries))

        if descendants:
            queries = get_json_field_queries(descendants, 'descendants', 'concept_id')
            queryset = queryset.filter(reduce(operator.or_, queries))

        if refset_id:
            queries = get_json_field_queries(refset_id, 'reference_set_memberships', 'refset_id')
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

    def get_required_fields(self, request, queryset, default_excluded_fields):
        """Fetch a subset of fields from the model, to be used like
        queryset.only(*fields), determined by the request's ``fields``
        query parameter.  If a request has a ``exclude_fields=true``
        query parameter, the the fields specified are excluded.

        For example, if a resource has the fields (id, name, age, location)

        Request
            /terminology/concepts?fields=id,preferred_term

        Response

            {
                "id": "<value>",
                "preferred_term": "<value>"
            }

        If the requested field is a JSON array,
        Request
            /terminology/concepts?fields=id,preferred_term,descriptions.term

        Response

            {
                "id": "<value>",
                "preferred_term": "<value>"
            }

        Request
        /terminology/concepts?fields=id,preferred_term&exclude_fields=true

        Response

            {
                "effective_time": "<value>",
                "active": "<value>",
                 ...
            }

        """
        existing_model_fields = set([field.name
                                     for field in
                                     queryset.model._meta.concrete_fields])

        fields = request.query_params.get('fields', None)

        exclude_fields = (
            request.query_params.get("exclude_fields", "f").lower() == "true"
        )
        show_full_model = (
            request.query_params.get(
                "full",
                "false").lower() == "true"
        )

        fields_param_not_set = fields is None or fields is ''

        if fields_param_not_set and not show_full_model:
            return list(existing_model_fields - default_excluded_fields)

        elif fields_param_not_set and show_full_model:
            return existing_model_fields

        fields = fields.split(",")

        allowed = set(fields)

        if exclude_fields:
            fields = list(existing_model_fields - allowed)

        if 'rank' in fields:
            fields.remove('rank')

        for field in fields:
            try:
                assert field.split('.')[0] in existing_model_fields
            except:
                raise APIException(detail="""\
The field: {} does not exist in the model: {}""".format(field, queryset.model.__name__))

        return fields

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
