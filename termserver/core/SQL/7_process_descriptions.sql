CREATE OR REPLACE FUNCTION process_descriptions(descs json[])
RETURNS description_result
AS $$
import ujson as json


def _get_main_descriptions():
    """Combine what would have been six loops into one ( time savings )"""
    descrs = []
    preferred_terms = []
    synonyms = []
    fsn = ''
    definition = ''
    preferred_term = ''

    for descr in [json.loads(descr) for descr in descs]:
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
