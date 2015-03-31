import django_filters


class ComponentFilter(django_filters.FilterSet):
    """Filters shared between concepts, descriptions and relationships"""
    release_date = django_filters.DateFilter(name="effective_time")
    active = django_filters.BooleanFilter(name="active")
