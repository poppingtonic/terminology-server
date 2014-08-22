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

    def _get_transitive_closure_map(type_id, is_inclusion_query=True):
        # Django's SQL parser does not like percent signs, so we cannot use string interpolation
        if is_inclusion_query:
            query = "SELECT DISTINCT(component_id), source_id, destination_id FROM snomed_relationship WHERE type_id IN (" + type_id + ")"
        else:
            query = "SELECT DISTINCT(component_id), source_id, destination_id FROM snomed_relationship WHERE type_id NOT IN (" + type_id + ")"

        map = defaultdict(list)
        for rel in plpy.execute(query):
            map[rel["destination_id"]].append(rel["source_id"])
        g = nx.MultiDiGraph(data=nx.from_dict_of_lists(map))
        if not nx.is_directed_acyclic_graph(g):
            raise Exception("We expected to have a directed acyclic graph")
        return g

    IS_A_PARENTS_TO_CHILDREN_GRAPH = _get_transitive_closure_map('116680003')
    PART_OF_PARENTS_TO_CHILDREN_GRAPH = _get_transitive_closure_map('123005000')
    OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH = _get_transitive_closure_map('116680003,123005000', is_inclusion_query=False)

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
