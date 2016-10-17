import os
import functools
import json
import datetime
from django.db import connection
from simplejson import load
from rest_framework.exceptions import APIException
from rest_framework.pagination import CursorPagination


def as_bool(val, default=True):
    assert default is False or default is True

    if type(val) is bool:
        return val
    elif val is None:
        return default
    try:
        p = json.loads(val.lower())
        assert p is False or p is True
        return p
    except ValueError as e:
        raise APIException(detail="""You requested a resource with ?active={},\
 which is not a boolean type. Depending on what you need, use ?active=True or \
?active=False.""".format(val))


@functools.lru_cache(maxsize=32)
def execute_query(query, param=None):
    """Executes a raw sql query, using a list of params, to prevent sql
    injection attacks. Caveat: This function should only be used in a
    read-only server, due to the likelihood of cache invalidation. If you
    really must use it, please remove the functools.lru_cache decorator."""

    cursor = connection.cursor()
    if param:
        try:
            cursor.execute(query, [param])
        except Exception as e:
            raise APIException(detail=e)
    else:
        try:
            cursor.execute(query)
        except Exception as e:
            raise APIException(detail=e)

    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        return []


def get_concept_relatives(relatives, concept_id):
    """Quick method to find all relatives of a concept. Returns a generator
    for fast iteration.

    The definition of 'get_ids_from_jsonb(jsonb, text)' is in
    'migrations/sql/final_load.sql'

    """
    assert relatives in ('parents', 'children', 'ancestors', 'descendants')
    concept_id = int(concept_id)

    query = """
select get_ids_from_jsonb({}, '{}')
    from snomed_denormalized_concept_view_for_current_snapshot
    where id = %s""".format(relatives, 'concept_id')
    relatives = (int(relative)
                 for relative in
                 execute_query(query, concept_id))
    return relatives


def parse_date_param(date_string, from_filter=False):
    if from_filter:
        return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
    else:
        return datetime.datetime.strptime(date_string, '%Y%m%d').date()


def _positive_int(integer_string):
    """
    Cast a string to a strictly positive integer.
    """
    ret = int(integer_string)
    if ret <= 0:
        raise ValueError()
    return ret


class ModifiablePageSizePagination(CursorPagination):
    def get_page_size(self, request):
        page_size_query_param = 'page_size'
        user_selected_page_size = request.query_params.get(page_size_query_param, None)

        if user_selected_page_size:
            try:
                return _positive_int(
                    user_selected_page_size
                )
            except (ValueError):
                raise APIException(detail="""You can't have a page_size less than or equal to 0. \
Please increase the page_size to something reasonable.""")
        else:
            return self.page_size


def get_language_name(language_code):
    iso_639_codes_file = os.getenv('ISO_639_CODES', '')

    with open(iso_639_codes_file) as f:
        iso_639_codes = load(f)
    return iso_639_codes[language_code]


UNIMPLEMENTED_RELEASE_STATUS_ERROR = """Request contains release_status=D\
 (developmental) or release_status=E (evaluation) in a query param, but \
there are no developmental or evaluation versions of this API yet."""
