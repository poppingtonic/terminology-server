CREATE OR REPLACE FUNCTION process_relationships(rels bigint[]) RETURNS text AS $$
import ujson as json

def _get_preferred_name(concept_id):
    # Unable to use string interpolation because Django's SQL parser will choke on the percent sign
    return plpy.execute("SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = " + str(concept_id))[0]["preferred_term"]

def _process_relationship(relationship):
    for rel in rels:
        return {
            "concept_id": rel,
            "concept_name": _get_preferred_name(rel)
        }

return json.dumps([_process_relationship(rel) for rel in json.loads(rels)])
$$ LANGUAGE plpythonu;
