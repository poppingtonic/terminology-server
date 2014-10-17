CREATE TYPE description_result AS (
    preferred_terms denormalized_description[],
    synonyms denormalized_description[],
    fully_specified_name text,
    definition text,
    preferred_term text
);
