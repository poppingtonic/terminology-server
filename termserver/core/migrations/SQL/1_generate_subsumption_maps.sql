CREATE OR REPLACE FUNCTION generate_subsumption_maps() RETURNS
TABLE(
  concept_id bigint,
  is_a_direct_parents text, is_a_parents text, is_a_direct_children text, is_a_children text,
  part_of_direct_parents text, part_of_parents text, part_of_direct_children text, part_of_children text,
  other_direct_parents text, other_parents text, other_direct_children text, other_children text
) AS $$
    from collections import defaultdict

    import json
    import networkx as nx

    def _get_transitive_closure_map(type_id, is_inclusion_query=True):
        # Django's SQL parser does not like percent signs, so we cannot use string interpolation
        if is_inclusion_query:
            query = "SELECT DISTINCT(component_id), source_id, destination_id FROM snomed_relationship WHERE type_id IN (" + type_id + ")"
        else:
            query = "SELECT DISTINCT(component_id), source_id, destination_id FROM snomed_relationship WHERE type_id NOT IN (" + type_id + ")"

        map = defaultdict(list)
        for rel in plpy.execute(query):
            map[rel["destination_id"]].append(rel["source_id"])
        return nx.MultiDiGraph(data=nx.from_dict_of_lists(map))

    IS_A_PARENTS_TO_CHILDREN_GRAPH = _get_transitive_closure_map('116680003')
    PART_OF_PARENTS_TO_CHILDREN_GRAPH = _get_transitive_closure_map('123005000')
    OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH = _get_transitive_closure_map('116680003,123005000', is_inclusion_query=False)

    # Work on the |is a| relationships
    def get_is_a_children_of(parent_id):
        if parent_id in IS_A_PARENTS_TO_CHILDREN_GRAPH:
            return json.dumps(list(nx.dag.descendants(IS_A_PARENTS_TO_CHILDREN_GRAPH, parent_id)))
        else:
            return json.dumps([])

    def get_is_a_direct_children_of(parent_id):
        if parent_id in IS_A_PARENTS_TO_CHILDREN_GRAPH:
            return json.dumps(IS_A_PARENTS_TO_CHILDREN_GRAPH.successors(parent_id))
        else:
            return json.dumps([])

    def get_is_a_parents_of(child_id):
        if child_id in IS_A_PARENTS_TO_CHILDREN_GRAPH:
            return json.dumps(list(nx.dag.ancestors(IS_A_PARENTS_TO_CHILDREN_GRAPH, child_id)))
        else:
            return json.dumps([])

    def get_is_a_direct_parents_of(child_id):
        if child_id in IS_A_PARENTS_TO_CHILDREN_GRAPH:
            return json.dumps(IS_A_PARENTS_TO_CHILDREN_GRAPH.predecessors(child_id))
        else:
            return json.dumps([])

    # Work on the |part of| relationships
    def get_part_of_children_of(parent_id):
        if parent_id in PART_OF_PARENTS_TO_CHILDREN_GRAPH:
            return json.dumps(list(nx.dag.descendants(PART_OF_PARENTS_TO_CHILDREN_GRAPH, parent_id)))
        else:
            return json.dumps([])

    def get_part_of_direct_children_of(parent_id):
        if parent_id in PART_OF_PARENTS_TO_CHILDREN_GRAPH:
            return json.dumps(PART_OF_PARENTS_TO_CHILDREN_GRAPH.successors(parent_id))
        else:
            return json.dumps([])

    def get_part_of_parents_of(child_id):
        if child_id in PART_OF_PARENTS_TO_CHILDREN_GRAPH:
            return json.dumps(list(nx.dag.ancestors(PART_OF_PARENTS_TO_CHILDREN_GRAPH, child_id)))
        else:
            return json.dumps([])

    def get_part_of_direct_parents_of(child_id):
        if child_id in PART_OF_PARENTS_TO_CHILDREN_GRAPH:
            return json.dumps(PART_OF_PARENTS_TO_CHILDREN_GRAPH.predecessors(child_id))
        else:
            return json.dumps([])

    # Work on the other kinds of relationships - not |is a| or |part of|
    def get_other_children_of(parent_id):
        if parent_id in OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH:
            return json.dumps(list(nx.dag.descendants(OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH, parent_id)))
        else:
            return json.dumps([])

    def get_other_direct_children_of(parent_id):
        if parent_id in OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH:
            return json.dumps(OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH.successors(parent_id))
        else:
            return json.dumps([])

    def get_other_parents_of(child_id):
        if child_id in OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH:
            return json.dumps(list(nx.dag.ancestors(OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH, child_id)))
        else:
            return json.dumps([])

    def get_other_direct_parents_of(child_id):
        if child_id in OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH:
            return json.dumps(OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH.predecessors(child_id))
        else:
            return json.dumps([])

    # Compose the return list
    RETURN_LIST = []
    for concept in plpy.execute("SELECT DISTINCT component_id FROM snomed_concept"):
        concept_id = concept["component_id"]
        RETURN_LIST.append((
            concept_id,
            get_is_a_direct_parents_of(concept_id),
            get_is_a_parents_of(concept_id),
            get_is_a_direct_children_of(concept_id),
            get_is_a_children_of(concept_id),
            get_part_of_direct_parents_of(concept_id),
            get_part_of_parents_of(concept_id),
            get_part_of_direct_children_of(concept_id),
            get_part_of_children_of(concept_id),
            get_other_direct_parents_of(concept_id),
            get_other_parents_of(concept_id),
            get_other_direct_children_of(concept_id),
            get_other_children_of(concept_id),
        ))

    return RETURN_LIST
$$ LANGUAGE plpythonu;
