CREATE TYPE description_result AS (
    preferred_terms denormalized_description[],
    synonyms denormalized_description[],
    fully_specified_name denormalized_description,
    definition denormalized_description,
    preferred_term denormalized_description
);
