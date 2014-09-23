CREATE OR REPLACE FUNCTION process_descriptions(descs json[])
RETURNS description_result
AS $$
import ujson as json


def _get_preferred_name(concept_id):
    # We cannot use string interpolation because Django's SQL parser does not like percent signs
    return plpy.execute("SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = " + str(concept_id))[0]["preferred_term"]


def _process_description(descr):
    return {
        "description_id": descr["component_id"],
        "type_id": descr["type_id"],
        "type_name": _get_preferred_name(descr["type_id"]),
        "module_id": descr["module_id"],
        "module_name": _get_preferred_name(descr["module_id"]),
        "case_significance_id": descr["case_significance_id"],
        "case_significance_name": _get_preferred_name(descr["case_significance_id"]),
        "term": descr["term"],
        "active": descr["active"]
    }


def _get_main_descriptions():
    """Combine what would have been six loops into one ( time savings )"""
    descrs = []
    preferred_terms = []
    synonyms = []
    fsn = ''
    definition = ''
    preferred_term = ''

    for descr in [json.loads(descr) for descr in descs]:
        # All descriptions
        descrs.append(_process_description(descr))

        # Preferred terms
        if descr["acceptability_id"] == 900000000000548007:
            preferred_terms.append(_process_description(descr))

        # Synonyms
        if descr["acceptability_id"] in [900000000000549004, None] and descr["type_id"] == 900000000000013009:
            synonyms.append(_process_description(descr))

        # Fully specified name
        if descr["type_id"] == 900000000000003001:
            fsn = descr["term"]

        # Definition
        if descr["type_id"] == 900000000000550004:
            definition = descr["term"]

        # Preferred term; we record the first one, but the UK one takes precedence
        if descr["acceptability_id"] == 900000000000548007 and not preferred_term:
            preferred_term = descr["term"]
        if descr["acceptability_id"] == 900000000000548007 and descr["refset_id"] == 999001251000000103:
            preferred_term = descr["term"]

    return (
        json.dumps(descrs),
        json.dumps(preferred_terms),
        json.dumps(synonyms),
        fsn,
        definition,
        preferred_term
    )

return _get_main_descriptions()
$$ LANGUAGE plpythonu;
