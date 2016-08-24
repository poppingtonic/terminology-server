from rest_framework.exceptions import APIException
from .utils import (parse_date_param,
                    as_bool,
                    UNIMPLEMENTED_RELEASE_STATUS_ERROR,
                    ModifiablePageSizePagination)


class GlobalFilterMixin(object):
    pagination_class = ModifiablePageSizePagination

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
