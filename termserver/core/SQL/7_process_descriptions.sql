CREATE OR REPLACE FUNCTION process_descriptions(descs json[])
RETURNS description_result
AS $$
import ujson as json


def _get_preferred_name(concept_id):
    # We cannot use string interpolation because Django's SQL parser does not like percent signs
    return plpy.execute("SELECT preferred_term FROM concept_preferred_terms WHERE concept_id = " + str(concept_id))[0]["preferred_term"]


def _process_description(descr):
    descr["type_name"] = _get_preferred_name(descr["type_id"])
    descr["module_name"] = _get_preferred_name(descr["module_id"])
    descr["case_significance_name"] = _get_preferred_name(descr["case_significance_id"])
    return descr


def _get_main_descriptions():
    """Combine what would have been six loops into one ( time savings )"""
    descrs = []
    preferred_terms = []
    synonyms = []
    fsn = ''
    definition = ''
    preferred_term = ''

    for descr in [_process_description(json.loads(descr)) for descr in descs]:
        descrs.append(descr)
        if descr["type_id"] == 900000000000003001:  # Fully specified name
            fsn = descr["term"]
        elif descr["type_id"] == 900000000000550004:  # Definition
            definition = descr["term"]
        elif descr["type_id"] == 900000000000013009:  # Synonym
            if descr["acceptability_id"] == 900000000000548007:
                preferred_terms.append(descr)
                if descr["refset_id"] == 999001251000000103:  # UK refset
                    preferred_term = descr["term"]
            else:
                synonyms.append(descr)

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
