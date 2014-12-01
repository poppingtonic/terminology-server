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
import networkx as nx


def _get_transitive_closure_map():
    """Load SNOMED relationships into a networkx directed multi graph"""
    g = nx.MultiDiGraph()
    relationships = plpy.execute(
        "SELECT destination_id, source_id, type_id "
        "FROM snomed_relationship WHERE active = True"
    )
    for rel in relationships:
        g.add_edge(
            rel["destination_id"], rel["source_id"],
            type_id=rel["type_id"]
        )
    return g

# The primary graph, and sub-graphs for various types
G = _get_transitive_closure_map()
IS_A = nx.DiGraph(
    (source, target, attr) for source, target, attr in G.edges_iter(data=True)
    if attr['type_id'] == 116680003
)
PART_OF = nx.DiGraph(
    (source, target, attr) for source, target, attr in G.edges_iter(data=True)
    if attr['type_id'] == 123005000
)
OTHER = nx.DiGraph(
    (source, target, attr) for source, target, attr in G.edges_iter(data=True)
    if attr['type_id'] not in [116680003, 123005000]
)


def get_relationships(concept_id):
    """Extract a single concept's relationships"""
    return (
        concept_id,
        IS_A.predecessors(concept_id),
        list(nx.dag.ancestors(IS_A, concept_id)),
        IS_A.successors(concept_id),
        list(nx.dag.descendants(IS_A, concept_id)),
        PART_OF.predecessors(concept_id) if concept_id in PART_OF else [],
        list(nx.dag.ancestors(PART_OF, concept_id)) if concept_id in PART_OF else [],
        PART_OF.successors(concept_id) if concept_id in PART_OF else [],
        list(nx.dag.descendants(PART_OF, concept_id)) if concept_id in PART_OF else [],
        OTHER.predecessors(concept_id) if concept_id in OTHER else [],
        list(nx.dag.ancestors(OTHER, concept_id)) if concept_id in OTHER else [],
        OTHER.successors(concept_id) if concept_id in OTHER else [],
        list(nx.dag.descendants(OTHER, concept_id)) if concept_id in OTHER else [],
    )

concepts = plpy.execute(
    "SELECT DISTINCT component_id FROM snomed_concept WHERE active = True")
return (get_relationships(concept["component_id"]) for concept in concepts)
$$ LANGUAGE plpythonu;
