__author__ = 'ngurenyaga'

"""
# Tactics
## Fuzzy / tolerant search
 * index the "list" fields e.g synonyms, preferred_terms as JSON arrays, not some form of separator delimited strings
 * the foundational technique is a filtered search, with the filters implementing the five types of filter:
   * parents - a comma separated list of SCTIDs; omit the comma if only one
   * children - a comma separated list of SCTIDs; omit the comma if only one
   * module - a comma separated list of SCTIDs; omit the comma if only one
   * primitive - boolean; true or false
   * active - boolean; true or false
 * template processing will be used to compose the JSON that will be sent; or should it be dictionary interpolation?
 * autocomplete queries: use the index-time n-gram approach; edge n-grams; maximum 20 characters, minimum 4
 * use the standard analyzer ( keep the English stopwords default )
 * the analyzed field ( field used for search ) should be the one with all active descriptions
 * no formal support for wildcards or user entered boolean operators
 * "full" queries: use a **common terms query** with the "and" operator for low frequency and "or" operator for high frequency; set the analyzer to standard? [ no stopwords ]?
 * suggestions: "did you mean" is a perfect use case for the term or phrase suggester
 * "more like this": a "more like this" query that operates on all active descriptions
 * paginate using from / size:
 ```
 {
    "from" : 0, "size" : 10, // these are the defaults, change them
    "query" : { "term" : { "user" : "kimchy" }}
 }
 ```

## Handling of synonyms
 * process SNOMED word equivalents table into a Solr style synonyms file
 * inline the synonyms into the mapping definition at index creation time ( do not create a standalone file )

## Choice of client
 * Mozilla ElasticUtils

"""

# TODO Create concepts index
# TODO Create within that index a mapping for concepts
# TODO Adjust materialized views to add properties that load JSON
# TODO Use notebooks to test and verify all materialized views
# TODO Perform sanity checks on concepts using UMLS UTS search engine
# TODO Break migrations up into individual files
# TODO Create a single "fab build" step that does everything up to indexing
# TODO Create a "fab backup" step that works with Google Object storage
# TODO Create a docker container build process
# TODO Fix process around doenaloading, preparing and updating UK release content
# TODO Implement API
# TODO Implement search
# TODO Implement pep8 checks in tests
# TODO Fix test coverage issues
