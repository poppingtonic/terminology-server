CREATE TYPE shortened_description AS (
    term text,
    acceptability_id bigint,
    refset_id bigint
);

CREATE OR REPLACE FUNCTION get_preferred_term(descs shortened_description[]) RETURNS text AS $$
    -- GB English is 900000000000508004
    -- UK English reference set is 999001251000000103
    -- UK Extension drug lang refset is 999000681000001101
    SELECT term FROM unnest(descs)
    WHERE acceptability_id = 900000000000548007
    AND refset_id IN (900000000000508004, 999001251000000103, 999000681000001101);
$$ LANGUAGE SQL;
