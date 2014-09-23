CREATE TYPE relationship_result AS (
    is_a_parents json,
    is_a_children json,
    is_a_direct_parents json,
    is_a_direct_children json,
    part_of_parents json,
    part_of_children json,
    part_of_direct_parents json,
    part_of_direct_children json,
    other_parents json,
    other_children json,
    other_direct_parents json,
    other_direct_children json
);

CREATE OR REPLACE FUNCTION process_relationships(sub snomed_subsumption)
RETURNS relationship_result AS $$
import ujson as json

def _expand(rels):
    return json.dumps([{
        "concept_id": concept_id,
        "concept_name": plpy.execute("SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = " + str(concept_id))[0]["preferred_term"]
    } for concept_id in rels] if rels else '[]')

return (
    _expand(sub["is_a_parents"]), _expand(sub["is_a_children"]),
    _expand(sub["is_a_direct_parents"]), _expand(sub["is_a_direct_children"]),
    _expand(sub["part_of_parents"]), _expand(sub["part_of_children"]),
    _expand(sub["part_of_direct_parents"]), _expand(sub["part_of_direct_children"]),
    _expand(sub["other_parents"]), _expand(sub["other_children"]),
    _expand(sub["other_direct_parents"]), _expand(sub["other_direct_children"])
)
$$ LANGUAGE plpythonu;
