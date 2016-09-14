REFSET_LIST_VIEW_DOCUMENTATION = """ # The Purpose of Reference Sets

## Simple Reference Set

A `446609009 | Simple type reference set |` allows a set of components
to be specified for inclusion or exclusion for a specified purpose. This
type of reference ret represents an extensional definition of a subset
of SNOMED CT components. Thus it can be used to fully enumerate a subset
of concepts, descriptions or relationships. An `extensional` definition
of a concept's subsets involves enumerating all the components in that
subset. See
[Wikipedia](https://en.wikipedia.org/wiki/Extensional_and_intensional_definitions#Extensional_definition)
for examples of exensional definitions outside SNOMED, as it may improve
your intuition for the word's usage here.


## Ordered Reference Set

An `447258008 | Ordered type reference set |` allows a collection of
components to be defined with a specified priority given a specified
ordering. This type of reference ret can also be used to specify ordered
associations between different components. These can be used to specify
several interrelated subsets of components and to define alternative
hierarchies for navigation and selection of concepts or descriptions.


## Attribute Value Reference Set

An `900000000000480006 | Attribute value type reference set |` allows a
value from a specified range to be associated with a component. This
type of reference set can be use for a range of purposes where there is
a requirement to provide additional information about particular
concepts, descriptions or relationships. For example, an
`900000000000480006 | Attribute value type reference set |` is used to
indicate the reason why a concepts has been *inactivated*.

## Simple Map Reference Set

A `900000000000496009 | Simple map reference set |` allows
representation of simple maps between SNOMED CT concepts and values in
other code systems. No constraints are put on the number of coding
schemes supported, the number of codes within a particular scheme mapped
to by a single SNOMED CT concept or the number of SNOMED CT concepts
mapping to a particular code. However, this type of reference set is
usually only appropriate where there is a close "one-to-one" mapping
between SNOMED CT concepts and coded values in anothe code system.

## Complex and Extended Map Reference Sets

A `447250001 | Complex map type reference set |` enables representation
of maps where each SNOMED CT concept may map to one or more codes in a
target scheme. The type of reference set supports the general set of
mapping data required to enable a target code to be selected at run-time
from a number of alternate codes. It supports target code selection by
accommodating the inclusion of machine readable rules and/or human
readable advice. An `609331003 | Extended map type reference set |` adds
an additional field to allow categorization of maps.

## Language Reference Sets

A `900000000000506000 | Language type reference set |` supports the
representation of language and dialects preferences for the use of
particular descriptions. The most common use case for this type of
reference set is to specify the acceptable and preferred terms for use
within a particular country or region. However, the same type of
reference set can also be used to represent preferences for use of
descriptions in a more specific context such as a clinical specialty,
organization or department.

## Query Specification Reference Sets

A `900000000000512005 | Query specification type reference set |` allows
a serialised query to represent the membership of a subset of SNOMED CT
components. A query contained in the reference set is run against the
content of SNOMED CT to produce a subset of concepts, descriptions or
relationships. The query is referred to an intensional definition of the
subset. It can be run against future releases of SNOMED CT to generate
an updated set of subset members.  The members of the resulting subset
may also be represented in an enumerated form as a Simple reference
set. An enumerated representation of a subset is referred to as an
extensional definition.

### Example usage

In the example below, "serialised query 1" is a text string that can be used to generate members
for Reference set 1, which is a simple member reference set (without any additional fields within its member
records).

#### Example rows from Query Specification Reference Set (as a Python dict)

    {'refsetId': '| Simple query specification |',
     'referencedComponentId': ' | Target reference set |',
     'query': ' Serialized text of the query...'}


#### Query language specification
The specification of the query language has yet to be defined / selected, but it should be capable
of:

+ Selecting concepts using primary fields, subsumption testing,
  relationships, relationship groups, set operators (union,
  intersection, excludes), and lexical query;

+ Selecting descriptions, relationships and reference sets using similar
  mechanisms;

+ Calculation of values for the reference set's extended
  fields. Identifying the version of the syntax and any language syntax
  variations.

+ Queries that support definitions for terminologies other than SNOMED
  CT should also be supported. For example, queries to link or include
  codes in ICD-10, ICD-11, ICPC and LOINC.

## Annotation Reference Set

An `900000000000516008 | Annotation type reference set |` allows text
strings to be associated with components for any specified purpose.

### Example usage (as a Python Dict)

    {'refsetId': '900000000000517004 | Associated image |',
     'referencedComponentId': '86174004 | Laparoscope |',
     'annotation': 'http://www.educationaldimensions.com/eLearn/endoscope/bigScope.html'}

## Association Reference Set

An `900000000000521006 | Association type reference set |` represents a
set of unordered associations of a particular type between components.

## Module Dependency Reference Set

The `900000000000534007 | Module dependency reference set |` represents
dependencies between different SNOMED CT release modules. In each case,
the dependency indicates which version of each particular module a given
version of the dependent module requires.

## Description Format Reference Set

The `900000000000538005 | Description format reference set |` specifies
the text format and maximum length of each supported description
type. This permits additional description types to be specified in
future in addition to the three existing description types (synonym,
fully specified name and textual definition).

"""
