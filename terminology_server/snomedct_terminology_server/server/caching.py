from django.contrib.sites.shortcuts import get_current_site
from rest_framework_extensions.key_constructor import (bits,
                                                       constructors)


class HTTPHOSTKeyBit(bits.KeyBitBase):
    """Augments a cache and ETag generation key by providing a string made of
the SNOMED server's domain name, and any request parameters provided by
the client.

    """
    def get_data(self, params, view_instance, view_method, request, args, kwargs):
        return '.'.join([
            get_current_site(request).domain,
            str(request.query_params),
            ])


class ListAPIKeyConstructor(constructors.KeyConstructor):
    """Constructs a custom cache key and ETag key using the HTTPHostKeyBit,
for ListAPIs"""
    unique_method_id = bits.UniqueMethodIdKeyBit()
    list_sql_query = bits.ListSqlQueryKeyBit()
    format = bits.FormatKeyBit()
    language = bits.LanguageKeyBit()
    http_host = HTTPHOSTKeyBit()
    pagination = bits.PaginationKeyBit()
    kwargs = bits.KwargsKeyBit()
    args = bits.ArgsKeyBit()


class RetrieveAPIKeyConstructor(constructors.KeyConstructor):
    """Constructs a custom cache key and ETag key using the HTTPHostKeyBit,
for RetrieveAPIs"""
    unique_method_id = bits.UniqueMethodIdKeyBit()
    retrieve_sql_query = bits.RetrieveSqlQueryKeyBit()
    format = bits.FormatKeyBit()
    language = bits.LanguageKeyBit()
    http_host = HTTPHOSTKeyBit()
    kwargs = bits.KwargsKeyBit()
    args = bits.ArgsKeyBit()
