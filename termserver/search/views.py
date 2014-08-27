# coding=utf-8
"""Helper functions for search"""
from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from elasticsearch.exceptions import ElasticsearchException
from .search_query import search

import logging

LOGGER = logging.getLogger(__name__)


def _get_first_value(input):
    """A helper that extracts the first value from a list - if it is a list passed in"""
    try:
        res = input[0]
        return res
    except:
        # Stupid except clause; guilty as charged
        LOGGER.debug("Unable to extract the first element from: (%s, %s)" % (input, type(input)))
        return input


class SearchAPIException(APIException):
    """Communicate errors that occur during search"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Programming error in search API invocation'


class ElasticsearchAPIException(APIException):
    """Communicate errors that occur during search"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Unable to communicate with Elasticsearch'


def validate_comma_separated_long_list(input):
    """Parse and separate comma separated SCTID List
    :param input:
    """
    # First, strip any trailing comma
    csl = input.rstrip(',')
    # Next, split on the comma
    tokens = csl.split(',')
    # Then, check that every input is a long / parseable into a long
    for token in tokens:
        try:
            long(token)
        except ValueError as e:
            raise SearchAPIException('Invalid long values in comma separated list: %s' % input)
    # No need to redo the token parsing in the calling code
    return tokens


def validate_comma_separated_bool_list(input):
    """Parse and separate comma separated list of "boolean" values i.e. True / False as strins
    :param input:
    """
    # First, strip any trailing comma
    csl = input.rstrip(',')
    # Next, split on the comma
    tokens = csl.split(',')
    # Then, check that every input is recognizable as True or False
    return_set = set()
    for token in tokens:
        if token.lower() not in ['true', 'false']:
            raise SearchAPIException('Invalid boolean values in comma separated list: %s' % input)
        return_set.add(True if token.lower() == 'true' else False)
    # No need to redo the token parsing in the calling code
    return list(return_set)


class SearchView(APIView):
    """
    This is the terminology search API.

    # How to use the API
    The API expects the query string as a 'query' parameter. This parameter is compulsory.

    This API takes the following filters ( as query parameters ):

    * `parents` - a comma separated list of SCTIDs; omit the comma if only one parent
    * `children` - same format as above
    * `modules` - same format as above
    * `include_primitive` - a boolean; the default behavior is to exclude primitive concepts
    * `include_inactive` - a boolean; the default behaviour is to exclude inactive concepts
    * `include_synonyms` - a boolean; the default behavior is to exclude synonyms from the search
    * `verbose` - a boolean; if True, show verbose query explanations

    The API also expects a keyword argument `search_type` - which should be either `full`
    ( the default ) or `autocomplete`.

    # Example queries
     * a plain search for malaria, with no filtering - `GET /search/full/?query=malaria`
    """
    # This particular view will be unauthenticated; it is a public service
    # Throttling may be introduced in future if abuse is a problem

    def check_permissions(self, request):
        """
        This particular view will completely bypass authentication and permissions

        This service should run "behind the firewall", and behind a proxy server.
        Almost every other service will rely on this API - authentication would be a chronic pain.
        If abuse is suspected, firewall based rate limiting can be used to protect the service.
        """
        LOGGER.debug('Not enforcing permissions for request to "%s"' % request.path)

    def get(self, request, search_type='full'):
        """
        This API only has a `get` endpoint

        :param request:
        :param search_type:
        :return:
        """
        # The parameters will be processed into this dictionary
        processed_params = defaultdict(list)

        # First, validate the search type
        if search_type not in ['full', 'autocomplete']:
            raise SearchAPIException('Unknown search type: %s' % search_type)

        # Extract and validate the parameters
        params = request.QUERY_PARAMS
        if 'query' not in params:
            raise SearchAPIException('This API expects a `query` parameter. None was supplied.')
        processed_params['query'] = params['query']

        for long_param_key in ['parents', 'children', 'modules']:
            if long_param_key in params:
                processed_params[long_param_key] = validate_comma_separated_long_list(params[long_param_key])

        for bool_param_key in ['include_primitive', 'include_inactive', 'include_synonyms', 'verbose']:
            if bool_param_key in params:
                processed_params[bool_param_key] = validate_comma_separated_bool_list(params[bool_param_key])

        # Delegate to the search helper function
        LOGGER.debug('Raw query parameters: %s' % str(params))
        LOGGER.debug('Processed query Parameters: %s' % str(processed_params))

        show_verbose_results = processed_params['verbose'] if 'verbose' in processed_params else False

        try:
            results = search(
                query_string=processed_params['query'],
                active=[True, False] if processed_params['include_inactive'] else [True],
                primitive=[True, False] if processed_params['include_primitive'] else [False],
                include_synonyms=True if processed_params['include_synonyms'] else False,
                module_ids=processed_params['modules'],
                parents=processed_params['parents'],
                children=processed_params['children'],
                verbose=show_verbose_results,
                query_type=search_type
            )

            # Post-process the results
            LOGGER.debug('\nResults: %s\n' % results['hits']['hits'])
            processed_results = {
                'suggestions': results['suggest']['descriptions'],
                'hits': [
                        {k : _get_first_value(v) for k, v in result['fields'].iteritems()}
                        for result in results['hits']['hits']
                ]
            }
            return Response(processed_results)
        except ElasticsearchException as ex:
            raise ElasticsearchAPIException('Unable to communicate to Elasticsearch because of: %s' % ex)

