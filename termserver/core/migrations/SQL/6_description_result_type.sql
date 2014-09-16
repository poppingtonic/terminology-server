CREATE TYPE description_result AS (
    descriptions json,
    preferred_terms json,
    synonyms json,
    fully_specified_name text,
    definition text,
    preferred_term text
);
