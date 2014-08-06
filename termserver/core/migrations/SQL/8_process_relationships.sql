CREATE OR REPLACE FUNCTION process_relationships(rels text) RETURNS text AS $$
import ujson as json

def _get_preferred_name(concept_id):
    # Unable to use string interpolation because Django's SQL parser will choke on the percent sign
    return plpy.execute("SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = " + str(concept_id[0]))["preferred_term"]

def _process_relationship(relationship):
    rel = json.loads(relationship)
    return {
        "relationship_id": rel["relationship_id"],
        "concept_id": rel["concept_id"],
        "concept_name": _get_preferred_name(rel["concept_id"])
    }

return json.dumps([_process_relationship(rel) for rel in json.loads(rels)])
$$ LANGUAGE plpythonu;
