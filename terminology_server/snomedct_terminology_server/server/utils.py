from django.db import connection
from django.db.utils import DataError
import functools
import json
import datetime
from rest_framework.exceptions import APIException


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

class GlobalFilterMixin(object):
    def get_queryset(self):
        queryset = super(GlobalFilterMixin, self).get_queryset()
        release_date = self.request.query_params.get('release_date', None)
        release_status = self.request.query_params.get('release_status', 'R')
        active = self.request.query_params.get('active', True)

        if as_bool(active) == True:
            queryset = queryset.filter(active=True)
        else:
            queryset = queryset.filter(active=False)

        if release_date:
            try:
                parsed_date = parse_date_param(release_date, from_filter=True)
                queryset = queryset.filter(effective_time=parsed_date)
            except ValueError as error:
                raise APIException(detail=error)
        else:
            pass

        if release_status == 'R':
            pass
        elif release_status == 'E' or release_status == 'D': # pragma: no cover
            raise APIException(detail=UNIMPLEMENTED_RELEASE_STATUS_ERROR)

        return queryset

UNIMPLEMENTED_RELEASE_STATUS_ERROR = """Request contains release_status=D\
 (developmental) or release_status=E (evaluation) in a query param, but \
there are no developmental or evaluation versions of this API yet."""
