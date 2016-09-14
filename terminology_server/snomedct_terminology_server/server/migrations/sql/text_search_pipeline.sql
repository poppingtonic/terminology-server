CREATE EXTENSION IF NOT EXISTS plv8;

CREATE TABLE description_terms AS SELECT word, nentry FROM
    ts_stat('SELECT to_tsvector(''simple'', term) FROM denormalized_description_for_current_snapshot where active = true');
CREATE INDEX unique_words_in_description_terms on description_terms (word);

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
