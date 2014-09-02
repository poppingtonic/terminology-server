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
SEARCH_SHORTCUT_TYPES = [
    'general', 'diseases', 'findings', 'symptoms', 'adverse_reactions',
    'procedures', 'operative_procedures', 'diagnostic_procedures',
    'prescription_procedures', 'dispensing_procedures',
    'drug_regimen_procedures', 'patient_history', 'family_history',
    'examination_findings', 'vital_signs', 'evaluation_procedures',
    'imaging_referrals', 'investigation_referrals', 'lab_referrals',
    'physiology_referrals', 'laboratory_procedures', 'imaging_procedures',
    'evaluation_findings', 'imaging_findings', 'specimens', 'chart_procedure',
    'administrative_procedure', 'admission_procedure', 'discharge_procedure',
    'body_structures', 'organisms', 'substances', 'drugs', 'vtms', 'vmps',
    'amps', 'vmpps', 'ampps'
]
SEARCH_TYPES = ['full', 'autocomplete']
SEARCH_LONG_PARAMS = ['parents', 'children', 'modules']
SEARCH_BOOL_PARAMS = [
    'include_primitive', 'include_inactive', 'include_synonyms', 'verbose']


def _get_first_value(inp):
    """Extracts the first value from a list - if a list passed in"""
    try:
        return inp[0]
    except:
        return inp


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
    # Check for null input
    if not input:
        return []
    # First, strip any trailing comma
    csl = input.rstrip(',')
    # Next, split on the comma
    tokens = csl.split(',')
    # Then, check that every input is a long / parseable into a long
    for token in tokens:
        try:
            long(token)
        except ValueError:
            raise SearchAPIException(
                'Invalid long values in comma separated list: %s' % input)
    # No need to redo the token parsing in the calling code
    return tokens


def validate_comma_separated_bool_list(input):
    """Parse and separate comma separated list of "boolean" values

    ( i.e. True / False input as strings )
    :param input:
    """
    # Check for null input
    if not input:
        return []
    # First, strip any trailing comma
    csl = input.rstrip(',')
    # Next, split on the comma
    tokens = csl.split(',')
    # Then, check that every input is recognizable as True or False
    return_set = set()
    for token in tokens:
        if token.lower() not in ['true', 'false']:
            raise SearchAPIException(
                'Invalid boolean values in comma separated list: %s' % input)
        return_set.add(True if token.lower() == 'true' else False)
    # No need to redo the token parsing in the calling code
    return list(return_set)


class SearchView(APIView):
    """
    This is the terminology search API.

    # How to use the API
    The API expects the query string as a **compulsory** 'query' parameter.

    This API takes the following filters ( as query parameters ):

    * `parents` - a comma separated list of SCTIDs; omit the comma if only one
    * `children` - same format as above
    * `modules` - same format as above
    * `include_primitive` - 'true' or 'false';
        the default is to exclude primitive concepts
    * `include_inactive` - 'true' or 'false';
        the default is to exclude inactive concepts
    * `include_synonyms` - 'true' or 'false';
        the default is to exclude synonyms
    * `verbose` - a boolean; if True, show verbose query explanations

    The API also expects a keyword argument `search_type` - one of `full`
    ( the default ) or `autocomplete`.

    # Example queries
     * unfiltered search for malaria - `GET /search/full/?query=malaria`
    """
    # This particular view will be unauthenticated; it is a public service
    # Throttling may be introduced in future if abuse is a problem

    def check_permissions(self, request):
        """
        This particular view will completely bypass auth and permissions

        This service should run "behind the firewall", and behind a proxy.
        Almost every other service will rely on this API - authentication
        would be a chronic pain. If abuse is suspected, firewall based rate
        limiting can be used to protect the service.
        """
        LOGGER.debug('Not enforcing permissions for "%s"' % request.path)

    def get(self, request, search_type='full', shortcut_type='general'):
        """
        This API only has a `get` endpoint

        :param request:
        :param search_type:
        :param shortcut_type
        :return:
        """
        # First, validate the search type
        if search_type not in SEARCH_TYPES:
            raise SearchAPIException('Unknown search type: %s' % search_type)

        # Next, vaidate the shortcut type
        if shortcut_type not in SEARCH_SHORTCUT_TYPES:
            raise SearchAPIException('Unknown shortcut: %s' % shortcut_type)

        # The parameters will be processed into this dictionary
        processed_params = defaultdict(list)

        # Extract and validate the parameters
        params = request.QUERY_PARAMS
        if 'query' not in params:
            raise SearchAPIException(
                'This API expects a `query` parameter. None was supplied.')
        processed_params['query'] = params['query']

        for long_param_key in SEARCH_LONG_PARAMS:
            if long_param_key in params:
                processed_params[long_param_key] = \
                    validate_comma_separated_long_list(params[long_param_key])

        for bool_param_key in SEARCH_BOOL_PARAMS:
            if bool_param_key in params:
                processed_params[bool_param_key] = \
                    validate_comma_separated_bool_list(params[bool_param_key])

        # Delegate to the search helper function
        LOGGER.debug('Raw query parameters: %s' % str(params))
        LOGGER.debug('Processed query Parameters: %s' % str(processed_params))

        show_verbose_results = processed_params['verbose'] \
            if 'verbose' in processed_params else False
        show_synonyms = True \
            if processed_params['include_synonyms'] else False
        show_primitive = [True, False] \
            if processed_params['include_primitive'] else [False]
        show_active = [True, False] \
            if processed_params['include_inactive'] else [True]

        try:
            results = search(
                query_string=processed_params['query'],
                active=show_active,
                primitive=show_primitive,
                include_synonyms=show_synonyms,
                module_ids=processed_params['modules'],
                parents=processed_params['parents'],
                children=processed_params['children'],
                verbose=show_verbose_results,
                query_type=search_type
            )

            # Post-process the results
            processed_results = {
                'suggestions': results['suggest']['descriptions'],
                'hits': [
                    {
                        k: _get_first_value(v)
                        for k, v in result['fields'].iteritems()
                    }
                    for result in results['hits']['hits']
                ]
            }
            return Response(processed_results)
        except ElasticsearchException as ex:
            raise ElasticsearchAPIException(
                'Unable to communicate to Elasticsearch because of: %s' % ex)
