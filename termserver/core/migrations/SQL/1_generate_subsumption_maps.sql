CREATE OR REPLACE FUNCTION generate_subsumption_maps() RETURNS
TABLE(
  concept_id bigint,
  is_a_direct_parents text, is_a_parents text, is_a_direct_children text, is_a_children text,
  part_of_direct_parents text, part_of_parents text, part_of_direct_children text, part_of_children text,
  other_direct_parents text, other_parents text, other_direct_children text, other_children text
) AS $$
    from collections import defaultdict
    from datetime import datetime

    import ujson as json
    import networkx as nx

    IS_A_PARENTS_TO_CHILDREN_GRAPH = defaultdict(set)
    PART_OF_PARENTS_TO_CHILDREN_GRAPH = defaultdict(set)
    OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH = defaultdict(set)

    def _get_transitive_closure_map(type_id, is_inclusion_query=True):
        # Django's SQL parser does not like percent signs, so we cannot use string interpolation
        if is_inclusion_query:
            query = "SELECT DISTINCT(component_id), source_id, destination_id FROM snomed_relationship WHERE type_id IN (" + type_id + ")"
        else:
            query = "SELECT DISTINCT(component_id), source_id, destination_id FROM snomed_relationship WHERE type_id NOT IN (" + type_id + ")"

        return nx.MultiDiGraph(
            data=nx.from_dict_of_lists({rel["destination_id"]:rel["source_id"] for rel in plpy.execute(query)})
        )

    def get_is_a_transitive_closure_map():
        IS_A_PARENTS_TO_CHILDREN_GRAPH = _get_transitive_closure_map('116680003')

    def get_part_of_transitive_closure_map():
        PART_OF_PARENTS_TO_CHILDREN_GRAPH = _get_transitive_closure_map('123005000')

    def get_other_relationships_transitive_closure_map():
        OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH = _get_transitive_closure_map('116680003,123005000', is_inclusion_query=False)

    # Work on the |is a| relationships
    def get_is_a_children_of(parent_id):
        return IS_A_PARENTS_TO_CHILDREN_GRAPH.descendants(parent_id)

    def get_is_a_direct_children_of(parent_id):
        return json.dumps(list(IS_A_PARENTS_TO_CHILDREN_MAP.get(parent_id, [])))

    def get_is_a_parents_of(child_id):
        return IS_A_CHILDREN_TO_PARENTS_GRAPH.ancestors(child_id)

    def get_is_a_direct_parents_of(child_id):
        return json.dumps(list(IS_A_CHILDREN_TO_PARENTS_MAP.get(child_id, [])))

    # Work on the |part of| relationships
    def get_part_of_children_of(parent_id):
        return PART_OF_PARENTS_TO_CHILDREN_GRAPH.descendants(parent_id)

    def get_part_of_direct_children_of(parent_id):
        return json.dumps(list(PART_OF_PARENTS_TO_CHILDREN_MAP.get(parent_id, [])))

    def get_part_of_parents_of(child_id):
        return PART_OF_CHILDREN_TO_PARENTS_GRAPH.ancestors(child_id)

    def get_part_of_direct_parents_of(child_id):
        return json.dumps(list(PART_OF_CHILDREN_TO_PARENTS_MAP.get(child_id, [])))

    # Work on the other kinds of relationships - not |is a| or |part of|
    def get_other_children_of(parent_id):
        return OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH.descendants(parent_id)

    def get_other_direct_children_of(parent_id):
        return json.dumps(list(OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_MAP.get(parent_id, [])))

    def get_other_parents_of(child_id):
        return OTHER_RELATIONSHIPS_PARENTS_TO_CHILDREN_GRAPH.ancestors(child_id)

    def get_other_direct_parents_of(child_id):
        return json.dumps(list(OTHER_RELATIONSHIPS_CHILDREN_TO_PARENTS_MAP.get(child_id, [])))

    # Compose the return list
    RETURN_LIST = []

    # Load the transitive closure maps into memory
    get_is_a_transitive_closure_map()
    get_part_of_transitive_closure_map()
    get_other_relationships_transitive_closure_map()

    concept_count_result = plpy.execute("SELECT count(DISTINCT component_id) FROM snomed_concept")
    concept_count = concept_count_result[0]["count"]

    done = 1
    start_time = datetime.now()
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
