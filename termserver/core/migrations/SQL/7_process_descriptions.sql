CREATE OR REPLACE FUNCTION process_descriptions(descs json[]) RETURNS description_result AS $$
import ujson as json
descriptions = [json.loads(descr) for descr in descs]

def _get_preferred_name(concept_id):
    # We cannot use string interpolation because Django's SQL parser does not like percent signs
    return plpy.execute("SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = " + concept_id)[0]["preferred_term"]

def _process_description(descr):
    return json.dumps({
        "description_id": descr["component_id"],
        "type_id": descr["type_id"],
        "type_name": _get_preferred_name(descr["type_id"]),
        "module_id": descr["module_id"],
        "module_name": _get_preferred_name(descr["module_id"]),
        "case_significance_id": descr["case_significance_id"],
        "case_significance_name": _get_preferred_name(descr["case_significance_id"]),
        "term": descr["term"],
        "active": descr["active"]
    })

def _get_fully_specified_name():
    for descr in descriptions:
        if descr["type_id"] == 900000000000003001:
            return descr["term"]

    # We should have returned a fully specified name by now
    raise Exception("No fully specified name found; this should not happen ( programming error )")

def _get_definition():
    for descr in descriptions:
        if descr["type_id"] == 900000000000550004:
            return descr["term"]

    # It is possible for the definition to be blank
    return ""

def _get_preferred_term():
    preferred_term = None

    # key "f1" is the term, key "f2" is the acceptability_id, key "f3" is the refset_id
    for descr in descs:
        desc_row = json.loads(descr)
        # Record the first preferred term that we see
        if desc_row["acceptability_id"] == 900000000000548007 and not preferred_term:
            preferred_term = desc_row["term"]
        # The UK Language reference set takes precedence over other reference sets and can overwrite prior values
        if desc_row["acceptability_id"] == 900000000000548007 and desc_row["refset_id"] == 999001251000000103:
            preferred_term = desc_row["term"]

    # We should have found a preferred term by now ( every concept should have one )
    if not preferred_term:
        raise Exception("Preferred term not found in: " + str(descs))

    # Finally, return it
    return preferred_term

return (
    json.dumps([
        _process_description(description)
        for description in descriptions
    ]),
    json.dumps([
        _process_description(description)
        for description in descriptions
        if description["acceptability_id"] == 900000000000548007
    ]),
    json.dumps([
        _process_description(description)
        for description in descriptions
        if description["acceptability_id"] in [900000000000549004, None] and description["type_id"] == 900000000000013009
    ]),
    _get_fully_specified_name(),
    _get_definition(),
    _get_preferred_term()
)
$$ LANGUAGE plpythonu;
