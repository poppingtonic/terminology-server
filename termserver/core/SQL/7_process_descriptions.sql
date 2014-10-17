CREATE OR REPLACE FUNCTION extract_fully_specified_name(descs denormalized_description[])
RETURNS denormalized_description AS $$
    SELECT * FROM unnest(descs) WHERE type_id = 900000000000003001 LIMIT 1;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION extract_definition(descs denormalized_description[])
RETURNS denormalized_description AS $$
    SELECT * FROM unnest(descs) WHERE type_id = 900000000000550004 LIMIT 1;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION extract_preferred_term(descs denormalized_description[])
RETURNS denormalized_description AS $$
    SELECT * FROM unnest(descs) WHERE type_id = 900000000000013009
    AND refset_id IN (900000000000508004, 999001251000000103, 999000681000001101)
    LIMIT 1;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION extract_preferred_terms(descs denormalized_description[])
RETURNS denormalized_description[] AS $$
    SELECT * FROM unnest(descs) WHERE type_id = 900000000000013009
    AND acceptability_id = 900000000000548007;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION extract_synonyms(descs denormalized_description[])
RETURNS denormalized_description[] AS $$
    SELECT * FROM unnest(descs) WHERE type_id = 900000000000013009
    AND acceptability_id != 900000000000548007;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION process_descriptions(descs denormalized_description[])
RETURNS description_result
AS $$
    SELECT
        extract_preferred_terms(descs),
        extract_synonyms(descs),
        extract_fully_specified_name(descs),
        extract_definition(descs),
        extract_preferred_term(descs);
$$ LANGUAGE SQL;
