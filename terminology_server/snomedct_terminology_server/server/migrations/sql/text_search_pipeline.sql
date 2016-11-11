CREATE EXTENSION IF NOT EXISTS plv8;

-- Converts all terms in the descriptions array of a concept to tsvectors
CREATE OR REPLACE FUNCTION get_tsvector_from_json(descriptions jsonb) RETURNS tsvector AS $get_tsvector$
DECLARE
   terms text;
BEGIN
   terms := concat_ws('|', VARIADIC ARRAY(select distinct jsonb_extract_path(jsonb_array_elements(descriptions), 'term')::text));
   return to_tsvector('english', terms);
END;
$get_tsvector$
LANGUAGE plpgsql IMMUTABLE;

-- Fast GIN indexes on tsvectors
CREATE INDEX gin_tsvector_descriptions ON snomed_denormalized_concept_view_for_current_snapshot USING gin (get_tsvector_from_json(descriptions));


-- Table of word equivalents
CREATE TABLE word_equivalents(
        word_block_number bigint,
        word_text text,
        word_type int,
        word_role int);

COPY word_equivalents(
    word_block_number,
    word_text,
    word_type,
    word_role)
FROM '/opt/snomedct_terminology_server/final_build_data/zres_WordEquivalents_en-US_INT_20150515.txt';

CREATE INDEX idx_word_text_word_equivalents ON word_equivalents (word_text);

CREATE OR REPLACE FUNCTION get_word_equivalents(text) RETURNS text[] AS $we$
DECLARE
  words text[];
BEGIN
  SELECT INTO words ARRAY(
    SELECT DISTINCT B.word_text
    FROM word_equivalents AS A
    JOIN word_equivalents AS B
    USING (word_block_number)
    WHERE A.word_text = $1
    AND B.word_type = 0);
  RETURN words;
END $we$
LANGUAGE plpgsql;

-- lifted from http://blog.databasepatterns.com/2014/08/postgresql-spelling-correction-norvig-plv8.html
-- plv8 is much faster than plpythonu, otherwise I'd have used a modified version of http://norvig.com/spell.py
CREATE OR REPLACE FUNCTION find_single_edits(text) RETURNS text[] LANGUAGE plv8 IMMUTABLE STRICT AS '
 var i, results = [], letters = "abcdefghijklmnopqrstuvwxyz".split("");

 // deletion
 for (i=0; i < $1.length; i++)
     results.push($1.slice(0, i) + $1.slice(i+1));

 // transposition
 for (i=0; i < $1.length-1; i++)
     results.push($1.slice(0, i) + $1.slice(i+1, i+2) + $1.slice(i, i+1) + $1.slice(i+2));

 // alteration
 for (i=0; i < $1.length; i++)
     letters.forEach(function (l) {
         results.push($1.slice(0, i) + l + $1.slice(i+1));
 });

 // insertion
 for (i=0; i <= $1.length; i++)
     letters.forEach(function (l) {
         results.push($1.slice(0, i) + l + $1.slice(i));
 });

 return results;
';

CREATE OR REPLACE FUNCTION find_double_edits(text[]) RETURNS text[] LANGUAGE plv8 IMMUTABLE STRICT AS '

 var edits1 = plv8.find_function("find_single_edits");

 var words = {}; //using object keys avoids duplicating things created by find_single_edits

 for(var i = 0; i < $1.length; i++) {

  var e2 = edits1($1[i]);

  for(var j = 0; j < e2.length; j++) {
   words[e2[j]] = null;
  }
 }

 return Object.keys(words);

';


-- This function is VOLATILE because of a temp table defined within it.
CREATE OR REPLACE FUNCTION correct(text) RETURNS text LANGUAGE plpgsql VOLATILE STRICT AS $$
DECLARE
 tmp text;
 e1 text[];
BEGIN

  -- don't spell-correct 2-3 letter words, return the original word
  IF length($1) <= 3 THEN
    RETURN $1;
  END IF;

  --if the word is in the corpus, return it:
  IF EXISTS( SELECT 1 FROM description_terms WHERE word = $1 ) THEN
    RETURN $1;
  END IF;

  --get all the 1-distance words:
  e1 = find_single_edits($1);

  SELECT
    word
  FROM description_terms
  WHERE
    word = any ( SELECT unnest( e1 ) )
  ORDER BY
    nentry DESC
  LIMIT 1
  INTO tmp;

  --IF there are 1-distance words that match, RETURN the most common one:
  IF found THEN
    RETURN tmp;
  END IF;

--using a session temp table is much faster than comparing to an array
  CREATE TEMP TABLE IF NOT EXISTS double_word_edits_cache ( word text );
  TRUNCATE TABLE double_word_edits_cache;

--get all the 2-distance edits and put in temp table:
  INSERT INTO double_word_edits_cache SELECT UNNEST( find_double_edits(e1) );

  SELECT
    description_terms.word
  FROM
    description_terms
    INNER JOIN double_word_edits_cache edits ON description_terms.word = edits.word
  ORDER BY description_terms.nentry DESC
  LIMIT 1
  INTO tmp;

  --IF there are 2-distance words that match, RETURN the most common one:
  IF found THEN
    RETURN tmp;
  END if;

  TRUNCATE TABLE double_word_edits_cache;

  --nothing found, RETURN the original word:
 RETURN $1;

END $$;
