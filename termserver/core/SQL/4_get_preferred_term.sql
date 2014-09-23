-- Return the first term in the array whose acceptability_id is 900000000000548007 and refset_id is 999001251000000103
-- Failing that, return the first term in the array whose acceptability_id is 900000000000548007


-- 98 seconds to populate concept_preferred_terms view with a cold cache
-- ( on the original development laptop )
-- 76 seconds with a warm cache
CREATE OR REPLACE FUNCTION get_preferred_term(descs json[]) RETURNS text AS $$
import ujson as json

preferred_term = None

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
    # Django's SQL parser chokes on percent signs, hence the string concatenation
    raise Exception("Preferred term not found in " + str(descs))

return preferred_term
$$ LANGUAGE plpythonu;
