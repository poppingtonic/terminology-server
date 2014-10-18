CREATE TYPE denormalized_description AS (
    component_id bigint,
    module_id bigint,
    module_name text,
    type_id bigint,
    type_name text,
    effective_time date,
    case_significance_id bigint,
    case_significance_name text,
    term text,
    language_code character varying(2),
    active boolean,
    acceptability_id bigint,
    acceptability_name text,
    refset_id bigint,
    refset_name text
);


CREATE TYPE description_result AS (
    preferred_terms denormalized_description[],
    synonyms denormalized_description[],
    fully_specified_name denormalized_description,
    definition denormalized_description,
    preferred_term denormalized_description
);
