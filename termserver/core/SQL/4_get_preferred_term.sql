CREATE OR REPLACE FUNCTION get_preferred_term(descs json[]) RETURNS text AS $$
import ujson as json

for descr in descs:
    desc_row = json.loads(descr)
    # Record the first preferred term that we see, but allow the UK language refset to override
    if desc_row["acceptability_id"] == 900000000000548007 and not preferred_term:
        preferred_term = desc_row["term"]
    elif desc_row["acceptability_id"] == 900000000000548007 and desc_row["refset_id"] == 999001251000000103:
        preferred_term = desc_row["term"]

return preferred_term
$$ LANGUAGE plpythonu;
