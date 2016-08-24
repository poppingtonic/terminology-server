from django.db import connection
import functools
import json
import datetime
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

    return result[0]


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
                raise APIException(detail="""You can't have a page_size of 0.
Please increase the page_size to something reasonable.""")
        else:
            return self.page_size


UNIMPLEMENTED_RELEASE_STATUS_ERROR = """Request contains release_status=D\
 (developmental) or release_status=E (evaluation) in a query param, but \
there are no developmental or evaluation versions of this API yet."""
