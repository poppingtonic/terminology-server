import os
import re
import gc
import functools
import json
import datetime
from django.db import connection, models
from simplejson import load
from rest_framework.exceptions import APIException
from rest_framework.pagination import CursorPagination
import networkx as nx

## Plotting the SNOMED graph
import matplotlib
matplotlib.use('SVG')

import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import pydot_layout
from matplotlib import pylab

# Non-interactive backend


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
    except ValueError:
        raise APIException(detail="""You're trying to get the boolean value of '{}',\
 which can't be used as boolean type. Depending on what you need, use True/true or \
False/false.""".format(val))


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


def get_concept_term_by_id_list(id_list):
    query = """
SELECT json_object(array_agg(id::text), array_agg(preferred_term))
    FROM snomed_denormalized_concept_view_for_current_snapshot WHERE id IN %s"""
    if id_list:
        tuple_of_ids = tuple(id_list)
        import pdb
        pdb.set_trace()
        concept_preferred_terms = execute_query(query, tuple_of_ids)
    return concept_preferred_terms


def get_json_field_queries(component_id_list, json_field_name, object_field):
    queries = []
    for component_id in component_id_list.split(','):
        try:
            component_id = int(component_id)
        except ValueError as e:
            raise APIException(detail="'{}' is not an integer. {}".format(component_id, e))
        queries.append(models.Q(**{'{}__array_contains_id'.format(json_field_name):
                                   (object_field, component_id)}))
    return queries


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


def replace_all_measurement_units(text):
    """Finds instances of measurements with spaces between the value and the
unit e.g. 5 mg and replaces them with the space removed e.g 5mg [5 mg ->
5mg]
    """
    measurement_regex = re.compile(r"(\d+ (MG|mg|kg|IU|iu))")
    substitutions = [[match.groups(0)[0], ''.join(match.groups(0)[0].split())]
                     for match in re.finditer(measurement_regex,
                                              text)]
    reps = {k[0]: k[1] for k in substitutions}

    for i, j in reps.items():
        text = text.replace(i, j)
    return text


def get_ancestry_graph(concept):
    adjacency_list_file = os.getenv('ADJACENCY_LIST_FILE', '')
    directed_graph = nx.DiGraph()
    SNOMED = nx.read_adjlist(adjacency_list_file, create_using=directed_graph)
    concept_ancestors = nx.ancestors(SNOMED, str(concept))
    ancestry_subgraph = SNOMED.subgraph(concept_ancestors)

    del SNOMED
    gc.collect()
    return ancestry_subgraph


def render_complete_graph(graph, file_name):
    plt.figure(num=None, figsize=(30, 30), dpi=160)
    plt.axis('off')
    fig = plt.figure(1)
    pos = pydot_layout(graph, prog='dot', format='svg')
    node_names = get_concept_term_by_id_list(graph.nodes())
    labeled_nodes = dict(zip(graph.nodes(),
                             list(map(lambda x: node_names[x] + ' | {} |'.format(x),
                                      graph.nodes()))))

    nx.draw_networkx_nodes(graph,pos)
    nx.draw_networkx_edges(graph,pos)

    nx.draw_networkx_labels(graph,pos, labels=labeled_nodes)

    cut = 5
    xmax = cut * max(xx for xx, yy in pos.values())
    ymax = cut * max(yy for xx, yy in pos.values())
    plt.xlim(0, xmax)
    plt.ylim(0, ymax)

    plt.savefig(file_name,bbox_inches="tight")
    pylab.close()
    del fig


UNIMPLEMENTED_RELEASE_STATUS_ERROR = """Request contains release_status=D\
 (developmental) or release_status=E (evaluation) in a query param, but \
there are no developmental or evaluation versions of this API yet."""
