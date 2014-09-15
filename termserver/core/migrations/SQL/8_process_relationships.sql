CREATE OR REPLACE FUNCTION process_relationships(rels bigint[]) RETURNS text AS $$
import ujson as json
import gc

plpy.notice('Processing ' + str(rels))

def _get_preferred_name(concept_id):
    # Unable to use string interpolation because Django's SQL parser will choke on the percent sign
    return plpy.execute("SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = " + str(concept_id))[0]["preferred_term"]

def _process_relationships():
    return [{
        "concept_id": rel,
        "concept_name": _get_preferred_name(rel)
    } for rel in rels]

# Earlier versions had pathological memory usage ( crashing with failed allocations )
gc.collect()

return json.dumps(_process_relationships() if rels else [])
$$ LANGUAGE plpythonu;
