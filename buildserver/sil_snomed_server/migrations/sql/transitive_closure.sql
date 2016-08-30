-- Get the effective_time of the latest SNOMED release
CREATE OR REPLACE FUNCTION get_tc_effective_time() RETURNS date AS $$
DECLARE
  tc_effective_time date;
BEGIN
  RETURN effective_time 
  from current_description_snapshot 
  where concept_id = 138875005 
  and module_id = 900000000000207008 
  order by effective_time 
  DESC limit 1;
END;
$$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION generate_single_snapshot_transitive_closure(effective_time date) RETURNS TEXT AS $$
DECLARE
  step int;
  rcount int;
BEGIN
-- Initialise by removing existing tables
  DROP TABLE IF EXISTS single_snapshot_transitive_closure;
  DROP INDEX IF EXISTS ix_tc_main;
  DROP INDEX IF EXISTS ix_tc_inv;
  DROP TABLE IF EXISTS tmp_tc1;
  DROP INDEX IF EXISTS ix_tc1;
  DROP INDEX IF EXISTS ix_tc_rel;
  DROP TABLE IF EXISTS batch_monitor;

  -- Create a table to allow batch process to be monitored (optional)
  CREATE TABLE batch_monitor (
    step integer NOT NULL PRIMARY KEY,
    "time" timestamp with time zone DEFAULT NULL,
    recs integer DEFAULT NULL,
    info character varying(45) DEFAULT NULL
  );
  -- Initialize step counter
  step=0;
  -- Record progress in batch_monitor table
  INSERT INTO batch_monitor(step,time,recs,info) VALUES(step,NOW(),0,'start') ON CONFLICT DO NOTHING;
  -- Create empty sct_transitive closure table
  CREATE TABLE single_snapshot_transitive_closure(
    subtype_id BIGINT,
    supertype_id BIGINT,
    effective_time date,
    active BOOLEAN,
    PRIMARY KEY (subtype_id, supertype_id, effective_time, active)
  );

  CREATE INDEX ix_tc_main ON  single_snapshot_transitive_closure (subtype_id,supertype_id);
  CREATE INDEX ix_tc_inv ON  single_snapshot_transitive_closure (supertype_id);
  -- Create temporary first level transitive closure table
  CREATE TEMPORARY TABLE tmp_tc1(
    subtype_id BIGINT,
    supertype_id BIGINT,
    PRIMARY KEY (subtype_id, supertype_id)
  );
  CREATE INDEX ix_tc1 ON  tmp_tc1 (supertype_id);

  -- Insert Values into First Level TC
  INSERT INTO tmp_tc1 (supertype_id, subtype_id) SELECT destination_id, source_id FROM current_relationship_snapshot WHERE active=true AND type_id = 116680003 ON CONFLICT DO NOTHING;
  -- Create Level A TEMPORARY TABLE for first iteration
  DROP TABLE IF EXISTS tmp_tcA;
  CREATE TEMPORARY TABLE tmp_tcA(
    subtype_id BIGINT,
    supertype_id BIGINT,
    PRIMARY KEY (subtype_id, supertype_id)
  );
  DROP INDEX IF EXISTS ix_tc2;
  CREATE INDEX ix_tc2 ON  tmp_tcA (supertype_id);
  -- Copy Level 1 in to Level A for first iteration
  INSERT INTO tmp_tcA (supertype_id, subtype_id) SELECT supertype_id, subtype_id FROM tmp_tc1 ON CONFLICT DO NOTHING;
  -- Start the Loop each pass adds 2 steps to the semantic distance
  <<tcloop>>
  LOOP
    RAISE NOTICE 'Beginning of loop. Step value: %', step;
  -- Increment the step count
    step := step+1;
    -- Count records in Level A
    rcount=(SELECT count('supertype_id') FROM tmp_tcA);
    RAISE NOTICE 'New loop starting. Current record count in tmp_tcA is: %', rcount;
    RAISE NOTICE 'We are in step %', step;
    -- Batch monitor report (optional)
    INSERT INTO batch_monitor(step,time,recs,info) VALUES(step,now(),rcount,'tcA') ON CONFLICT DO NOTHING;
    -- If Level A empty then quit here
    IF rcount=0 THEN
      RAISE NOTICE 'Early exit, no records in tmp_tcA. We are in step %', step;
      EXIT tcloop;
    END IF;
    -- Append Level A records to final TC table
    INSERT INTO single_snapshot_transitive_closure (supertype_id, subtype_id, effective_time, active)
      SELECT supertype_id, subtype_id, date(effective_time), True
      FROM tmp_tcA ON CONFLICT DO NOTHING;

    -- Count records in final TC table after appending Level A records
    RAISE NOTICE 'After appending level A, the record count of final TC table: %', (select count(*) from single_snapshot_transitive_closure);
    -- Create Level B temporary table for this iteration (adds 1 to semantic distance)
    DROP TABLE IF EXISTS tmp_tcB;
    CREATE TEMPORARY TABLE tmp_tcB(
      subtype_id BIGINT,
      supertype_id BIGINT,
      PRIMARY KEY (subtype_id, supertype_id));

    DROP INDEX IF EXISTS ix_tc3;
    CREATE INDEX ix_tc3 ON tmp_tcB (supertype_id);

    -- Insert A+1 into B
    INSERT INTO tmp_tcB (supertype_id, subtype_id)
      SELECT t.supertype_id, t1.subtype_id
      FROM tmp_tcA t
      INNER JOIN tmp_tc1 as t1
        ON t.subtype_id=t1.supertype_id
      LEFT OUTER JOIN single_snapshot_transitive_closure AS tc
        ON t.supertype_id=tc.supertype_id AND t1.subtype_id=tc.subtype_id
      WHERE tc.subtype_id is null ON CONFLICT DO NOTHING;

    RAISE NOTICE 'size of tmp_tcB: %', (SELECT count(*) from tmp_tcB);
    -- Level B empty then quit here
    step := step + 1;
    -- Level A empty then quit here
    rcount = (SELECT count(supertype_id) FROM tmp_tcB);
    INSERT INTO batch_monitor (step,time,recs,info)
      VALUES(step,now(),rcount,'tcB');
    IF rcount=0 THEN
      RAISE NOTICE 'Early exit, no records in tmp_tcB. We are in step %', step;
      EXIT tcloop;
    END IF;
    -- Append Level B to final TC table
    INSERT INTO single_snapshot_transitive_closure (supertype_id, subtype_id, effective_time,active)
      SELECT supertype_id, subtype_id, date(effective_time),True FROM tmp_tcB;
    -- Create Level A temporary table for next iteration
    DROP TABLE IF EXISTS tmp_tcA;
    CREATE TEMPORARY TABLE tmp_tcA (
      subtype_id BIGINT,
      supertype_id BIGINT,
      PRIMARY KEY (subtype_id, supertype_id));

    DROP INDEX IF EXISTS ix_tc4;
    CREATE INDEX ix_tc4 ON tmp_tcA (supertype_id);
    -- Insert B+1 into A
    INSERT INTO tmp_tcA (supertype_id, subtype_id)
      SELECT t.supertype_id, t1.subtype_id
      FROM tmp_tcB t
      INNER JOIN tmp_tc1 AS t1
        ON t.subtype_id=t1.supertype_id
      LEFT OUTER JOIN single_snapshot_transitive_closure As tc
        ON t.supertype_id=tc.supertype_id AND t1.subtype_id=tc.subtype_id
      WHERE tc.subtype_id is null ON CONFLICT DO NOTHING;
  END LOOP;

  RETURN 'ok';
END;
$$ LANGUAGE plpgsql;
-- END OF FUNCTION CREATION
-- RUN THE CREATED FUNCTION
EXPLAIN ANALYZE SELECT * FROM generate_single_snapshot_transitive_closure(get_tc_effective_time());
