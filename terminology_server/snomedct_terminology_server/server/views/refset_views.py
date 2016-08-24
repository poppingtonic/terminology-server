from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import OrderingFilter

from ..docs import REFSET_LIST_VIEW_DOCUMENTATION

from ..filters import GlobalFilterMixin

from ..search import CommonSearchFilter
from ..serializers import serialized_refset


def generate_refset_list_view(refset_model):
    # list_view
    name = refset_model.__name__.replace('DenormalizedView', '')
    list_view_name = name + "s"
    list_view_attrs = {}

    def get_queryset(self):
        refsets = refset_model.objects.all()
        return refsets

    list_view_attrs['__doc__'] = REFSET_LIST_VIEW_DOCUMENTATION
    list_view_attrs['get_queryset'] = get_queryset
    list_view_attrs['serializer_class'] = serialized_refset(refset_model)
    list_view_attrs['filter_backends'] = (OrderingFilter, CommonSearchFilter)
    list_view_attrs['ordering'] = ('id',)
    list_view_attrs['search_fields'] = ('%refset_name',)

    list_view_cls = type(
        list_view_name,
        (GlobalFilterMixin,
         ListAPIView,),
        list_view_attrs)
    return list_view_cls


def generate_refset_module_list_view(refset_model):
    # list_view
    name = refset_model.__name__.replace('DenormalizedView', '')
    list_view_name = name + "s" + "ByModuleId"
    list_view_attrs = {}
    list_view_attrs['serializer_class'] = serialized_refset(refset_model)

    def get_queryset(self):
        module_id = self.kwargs.get('module_id')
        refsets = refset_model.objects.filter(module_id=module_id)
        return refsets

    list_view_attrs['get_queryset'] = get_queryset
    list_view_attrs['filter_backends'] = (OrderingFilter, CommonSearchFilter)
    list_view_attrs['ordering'] = ('id',)

    list_view_cls = type(
        list_view_name,
        (GlobalFilterMixin,
         ListAPIView,),
        list_view_attrs)
    return list_view_cls


def generate_refset_detail_view(refset_model):
    # detail view
    name = refset_model.__name__.replace('DenormalizedView', '')
    detail_view_name = name + "DetailView"
    detail_view_attrs = {}

    detail_view_attrs['__doc__'] = """

    Showing individual {}s, using the UUID as the `pk`
    """.format(name)

    detail_view_attrs['serializer_class'] = serialized_refset(refset_model)

    detail_view_attrs['lookup_field'] = 'id'

    detail_view_attrs['queryset'] = refset_model.objects.all()

    detail_view_cls = type(
        detail_view_name,
        (GlobalFilterMixin,
         RetrieveAPIView,),
        detail_view_attrs)
    return detail_view_cls
