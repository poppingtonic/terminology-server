CREATE EXTENSION IF NOT EXISTS plpythonu;
CREATE OR REPLACE FUNCTION generate_subsumption_maps() RETURNS
TABLE(
  concept_id bigint,
  is_a_direct_parents bigint[], is_a_parents bigint[],
  is_a_direct_children bigint[], is_a_children bigint[],
  part_of_direct_parents bigint[], part_of_parents bigint[],
  part_of_direct_children bigint[], part_of_children bigint[],
  other_direct_parents bigint[], other_parents bigint[],
  other_direct_children bigint[], other_children bigint[]
) AS $$
    import gc
    import traceback
    import networkx as nx

    from collections import defaultdict

    def _check(g):
        """Perform a series of sanity checks"""
        if not nx.is_directed(g):
            raise Exception("The graph is not directed")

        if not nx.is_directed_acyclic_graph(g):
            raise Exception("We expected to have a directed acyclic graph")

    def _print_debug_information(g, map_type=''):
        """Debugging aid; left in because it might still be needed in future"""
        plpy.info("Overall graph information: " + nx.info(g))
        plpy.info("Root node information: " + nx.info(g, n=138875005))

    def _get_transitive_closure_map():
        """Load SNOMED relationships into a networkx directed multi graph"""
        g = nx.MultiDiGraph()
        relationships = plpy.execute(
            "SELECT destination_id, source_id, type_id "
            "FROM snomed_relationship WHERE active = True"
        )
        for rel in relationships:
            g.add_edge(
                rel["destination_id"], rel["source_id"], type_id=rel["type_id"]
            )
        if relationships.nrows():
            _check(g)
            _print_debug_information(g, map_type)
        nx.freeze(g)
        return g

    RELATIONSHIP_GRAPH = _get_transitive_closure_map()

    def get_relationships(concept_id):
        """Extract a single concept's relationships"""
        descendants = nx.dag.descendants(RELATIONSHIP_GRAPH, concept_id)
        direct_children = RELATIONSHIP_GRAPH.successors(concept_id)
        ancestors = nx.dag.ancestors(RELATIONSHIP_GRAPH, concept_id)
        direct_parents = RELATIONSHIP_GRAPH.predecessors(concept_id)
        return (
            concept_id,
            # |is a| relationships
            filter(direct_parents, lambda i: i['type_id'] == 116680003),
            filter(ancestors, lambda i: i['type_id'] == 116680003),
            filter(direct_children, lambda i: i['type_id'] == 116680003),
            filter(descendants, lambda i: i['type_id'] == 116680003),
            # |part of| relationships
            filter(direct_parents, lambda i: i['type_id'] == 123005000),
            filter(ancestors, lambda i: i['type_id'] == 123005000),
            filter(direct_children, lambda i: i['type_id'] == 123005000),
            filter(descendants, lambda i: i['type_id'] == 123005000),
            # relationships other than |is a| and |part of|
            filter(direct_parents,
                lambda i: i['type_id'] not in [116680003,123005000]),
            filter(ancestors,
                lambda i: i['type_id'] not in [116680003,123005000]),
            filter(direct_children,
                lambda i: i['type_id'] not in [116680003,123005000]),
            filter(descendants,
                lambda i: i['type_id'] not in [116680003,123005000])
        )

    concepts = plpy.execute("SELECT DISTINCT component_id FROM snomed_concept")
    return (get_relationships(concept["component_id"]) for concept in concepts)
$$ LANGUAGE plpythonu;
