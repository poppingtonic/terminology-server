__author__ = 'ngurenyaga'


# TODO Create concepts index
# TODO Create within that index a mapping for concepts; the combined descriptions field should be the only analyzed fields
# TODO Synonyms - process SNOMED word equivalents into synonyms
# TODO Create custom analyzer for synonyms and set it up as the query time analyzer
# TODO Ensure that all queries have pagination - with 25 items as our default
# TODO "full" queries: use a **common terms query** with the "and" operator for low frequency and "or" operator for high frequency; index analyzer to standard
# TODO Add autocomplete field to mapping; edge-ngram, 3-20 characters
# TODO Add query template, with support for filtering by parents, children, module, primitive, active
# TODO Ensure that synonym support can be turned on/off via query parameter
# TODO Incorporate phrase suggester into all searches
# TODO Incorporate "more like this" into all searches
# TODO Use notebooks to test and verify all materialized views
# TODO Perform sanity checks on concepts using UMLS UTS search engine
# TODO Create a single "fab build" step that does everything up to indexing
# TODO Create a "fab backup" step that works with Google Object storage
# TODO Create a docker container build process
# TODO Fix process around downaloading, preparing and updating UK release content
# TODO Implement API
# TODO Implement search
# TODO Implement pep8 checks in tests
# TODO Fix test coverage issues
