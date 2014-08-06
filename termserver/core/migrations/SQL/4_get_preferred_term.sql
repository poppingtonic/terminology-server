-- The preferred term is - by a wide margin - the most queried concept attribute
CREATE OR REPLACE FUNCTION get_preferred_term(descs json[]) RETURNS text AS $$
import ujson as json

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
   raise Exception("Preferred term not found in: %s" % descs)

return preferred_term
$$ LANGUAGE plpythonu;
