-- We need this custom type so that we can aggregate all the information that relates to one description togethe
CREATE TYPE description AS (
    component_id bigint,
    module_id bigint,
    type_id bigint,
    effective_time date,
    case_significance_id bigint,
    term text,
    language_code character varying(2),
    active boolean,
    acceptability_id bigint,
    refset_id bigint
);
