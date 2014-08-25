CREATE EXTENSION plpythonu;
CREATE OR REPLACE FUNCTION generate_subsumption_maps() RETURNS
TABLE(
  concept_id bigint,
  is_a_direct_parents bigint[], is_a_parents bigint[], is_a_direct_children bigint[], is_a_children bigint[],
  part_of_direct_parents bigint[], part_of_parents bigint[], part_of_direct_children bigint[], part_of_children bigint[],
  other_direct_parents bigint[], other_parents bigint[], other_direct_children bigint[], other_children bigint[]
) AS $$
    from collections import defaultdict
    import networkx as nx
    import gc
    import traceback

    def _check(g):
        """Perform a series of sanity checks"""
        if not nx.is_directed(g):
            raise Exception("The graph is not directed")

        if not nx.is_directed_acyclic_graph(g):
            raise Exception("We expected to have a directed acyclic graph")

    def _print_debug_information(g):
        """Debugging aid; left in because it might still be needed in future"""
        plpy.info("Overall graph information: " + nx.info(g))
        plpy.info("Root node information: " + nx.info(g, n=138875005))

    def _get_transitive_closure_map(type_id, is_inclusion_query=True, map_type=''):
        # Django's SQL parser does not like percent signs, so we cannot use string interpolation
        if is_inclusion_query:
            query = "SELECT destination_id, source_id FROM snomed_relationship WHERE active = True AND type_id IN (" + type_id + ")"
        else:
            query = "SELECT destination_id, source_id FROM snomed_relationship WHERE active = True AND type_id NOT IN (" + type_id + ")"

        g = nx.MultiDiGraph()
        relationships = plpy.execute(query)
        for rel in relationships:
            g.add_edge(rel["source_id"], rel["destination_id"])
        plpy.info("Map type: " + map_type)
        plpy.info("Simple Cycles: " + str(list(nx.simple_cycles(g))))
        nx.freeze(g)

        if relationships.nrows():
            # Do not run the checks when the database is empty e.g on initial migration in a new database
            _check(g)
            _print_debug_information(g)

        # use nx.simple_cycles(g) to debug
        # all_simple_paths(G, source, target, cutoff=None)
        # http://networkx.github.io/documentation/networkx-1.9/reference/algorithms.traversal.html has good stuff
        return g

    IS_A_PARENTS_TO_CHILDREN_GRAPH = _get_transitive_closure_map('116680003', map_type='IS A')
    PART_OF_PARENTS_TO_CHILDREN_GRAPH = _get_transitive_closure_map('123005000', map_type='PART OF')
    OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH = _get_transitive_closure_map('116680003,123005000',is_inclusion_query=False, map_type='OTHER')

    # Work on the |is a| relationships
    def get_is_a_children_of(parent_id):
        if parent_id in IS_A_PARENTS_TO_CHILDREN_GRAPH:
            return list(nx.dag.descendants(IS_A_PARENTS_TO_CHILDREN_GRAPH, parent_id))

    def get_is_a_direct_children_of(parent_id):
        if parent_id in IS_A_PARENTS_TO_CHILDREN_GRAPH:
            return IS_A_PARENTS_TO_CHILDREN_GRAPH.successors(parent_id)

    def get_is_a_parents_of(child_id):
        if child_id in IS_A_PARENTS_TO_CHILDREN_GRAPH:
            return list(nx.dag.ancestors(IS_A_PARENTS_TO_CHILDREN_GRAPH, child_id))

    def get_is_a_direct_parents_of(child_id):
        if child_id in IS_A_PARENTS_TO_CHILDREN_GRAPH:
            return IS_A_PARENTS_TO_CHILDREN_GRAPH.predecessors(child_id)

    # Work on the |part of| relationships
    def get_part_of_children_of(parent_id):
        if parent_id in PART_OF_PARENTS_TO_CHILDREN_GRAPH:
            return list(nx.dag.descendants(PART_OF_PARENTS_TO_CHILDREN_GRAPH, parent_id))

    def get_part_of_direct_children_of(parent_id):
        if parent_id in PART_OF_PARENTS_TO_CHILDREN_GRAPH:
            return PART_OF_PARENTS_TO_CHILDREN_GRAPH.successors(parent_id)

    def get_part_of_parents_of(child_id):
        if child_id in PART_OF_PARENTS_TO_CHILDREN_GRAPH:
            return list(nx.dag.ancestors(PART_OF_PARENTS_TO_CHILDREN_GRAPH, child_id))

    def get_part_of_direct_parents_of(child_id):
        if child_id in PART_OF_PARENTS_TO_CHILDREN_GRAPH:
            return PART_OF_PARENTS_TO_CHILDREN_GRAPH.predecessors(child_id)

    # Work on the other kinds of relationships - not |is a| or |part of|
    def get_other_children_of(parent_id):
        if parent_id in OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH:
            return list(nx.dag.descendants(OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH, parent_id))

    def get_other_direct_children_of(parent_id):
        if parent_id in OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH:
            return OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH.successors(parent_id)

    def get_other_parents_of(child_id):
        if child_id in OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH:
            return list(nx.dag.ancestors(OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH, child_id))

    def get_other_direct_parents_of(child_id):
        if child_id in OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH:
            return OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH.predecessors(child_id)

    # Return via a "lazy" generator; defer memory use as much as possible
    gc.collect()  # Strange inclusion? You bet. For a reason.
    return (
        (
            concept["component_id"],
            get_is_a_direct_parents_of(concept["component_id"]) or [],
            get_is_a_parents_of(concept["component_id"]) or [],
            get_is_a_direct_children_of(concept["component_id"]) or [],
            get_is_a_children_of(concept["component_id"]) or [],
            get_part_of_direct_parents_of(concept["component_id"]) or [],
            get_part_of_parents_of(concept["component_id"]) or [],
            get_part_of_direct_children_of(concept["component_id"]) or [],
            get_part_of_children_of(concept["component_id"]) or [],
            get_other_direct_parents_of(concept["component_id"]) or [],
            get_other_parents_of(concept["component_id"]) or [],
            get_other_direct_children_of(concept["component_id"]) or [],
            get_other_children_of(concept["component_id"]) or []
        ) for concept in plpy.execute("SELECT DISTINCT component_id FROM snomed_concept")
    )
$$ LANGUAGE plpythonu;
