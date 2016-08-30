from rest_framework.exceptions import APIException
from rest_framework_extensions.etag.mixins import ReadOnlyETAGMixin
from .utils import (parse_date_param,
                    as_bool,
                    UNIMPLEMENTED_RELEASE_STATUS_ERROR,
                    ModifiablePageSizePagination)


class GlobalFilterMixin(ReadOnlyETAGMixin):
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
