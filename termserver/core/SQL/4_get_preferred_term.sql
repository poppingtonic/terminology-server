CREATE TYPE shortened_description AS (
    term text,
    acceptability_id bigint,
    refset_id bigint
);

CREATE OR REPLACE FUNCTION get_preferred_term(shortened_description[]) RETURNS text AS $$
    SELECT term FROM unnest($1)
    WHERE acceptability_id = 900000000000548007
    AND refset_id = 999001251000000103;
$$ LANGUAGE SQL;
