import os
import logging
import collections
from itertools import groupby
from operator import itemgetter
from wsgiref.util import FileWrapper
from django.http import HttpResponse
from rest_framework.exceptions import APIException
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import OrderingFilter

from ..serializers import REFSET_MODELS

from ..utils import (
    as_bool,
    execute_query,
    parse_date_param,
    get_concept_relatives
)

from ..filters import GlobalFilterMixin, JSONFieldFilter, SearchOrderingFilter

from snomedct_terminology_server.server.models import (
    Concept,
    Description,
    Relationship,
    TransitiveClosure
)

from snomedct_terminology_server.server.serializers import (ConceptListSerializer,
                                                            ConceptDetailSerializer,
                                                            DescriptionListSerializer,
                                                            DescriptionDetailSerializer,
                                                            RelationshipSerializer,
                                                            TransitiveClosureSerializer)

logger = logging.getLogger(__name__)


def releases(release_type='international_release'):
    """Information about the current and past releases

    Release information is held in the root concept in the following
    manner:

    * the root concept has a current synonym that contains information
    about the release
    * the synonyms representing earlier release are distributed as
    inactive descriptions

    The syntax is as follows:

     * Example: SNOMED Clinical Terms version: 20020131 [R] (first release)
     * Syntax: SNOMED Clinical Terms version: yyyymmdd [status] (descr.)
       * yyyymmdd is the release date, in ISO format
       * status is one of R (release), D (developmental), E (evaluation)
       * descr. is an **optional** free text description
    """
    try:
        assert release_type in ('international_release', 'drug_extension', 'clinical_extension')
    except AssertionError:
        raise APIException(
            detail="Please select either 'international', 'drug_extension' or 'clinical_extension'")
    # Every concept's denormalized view includes inactive descriptions
    RELEASE_STATUSES = {
        'R': 'Released',
        'D': 'Development',
        'E': 'Evaluation'
    }

    root_concept_descriptions = Description.objects.filter(
        concept_id=138875005
    )
    description_terms = [description.term
                         for description
                         in root_concept_descriptions]
    international_release_descriptions = [
        description.replace('SNOMED Clinical Terms version: ', '')
        for description in description_terms
        if 'SNOMED Clinical Terms version: ' in description
    ]

    clinical_extension_descriptions = [
        description for description in description_terms
        if 'clinical extension' in description
    ]

    sorted_clinical_extension_descriptions = sorted(clinical_extension_descriptions, reverse=True)
    current_clinical_release = sorted_clinical_extension_descriptions[0]

    drug_extension_description_terms = [
        description for description in description_terms
        if 'drug extension' in description
    ]

    # sort descriptions by the first 8 numbers after the '_' in the description term
    # e.g. '20160525' in 21.3.0_20160525000001 UK drug extension
    sorted_terms = sorted(drug_extension_description_terms,
                          key=lambda x: x.split('_')[1][0:8],
                          reverse=True)

    # group sorted terms by major version and get the first item of the
    # group, to find the latest release in each version group e.g. '21' in
    # 21.3.0_20160525000001 UK drug extension

    latest_drug_extension_version_groups = []
    for k, g in groupby(sorted_terms, key=lambda x: x[0:2]):
        latest_drug_extension_version_groups.append(list(g)[0])
    current_drug_release = latest_drug_extension_version_groups[0]

    releases = sorted([
        {
            'release_date': parse_date_param(description[0:8]).isoformat(),
            'release_status': RELEASE_STATUSES[description[10]],
            'release_description': description[14:-1]
        } for description in international_release_descriptions
    ], key=itemgetter('release_date'), reverse=True)

    if release_type == 'drug_extension':
        return current_drug_release
    elif release_type == 'clinical_extension':
        return current_clinical_release
    else:
        return releases


@api_view(['GET'])
def api_root(request, format=None):
    """# Introduction

When a medical practitioner (doctor, nurse, lab-tech etc.) is looking at
a patient chart, she is looking at terms describing the patient's
condition. These could be terms like 'OGTT', which stands for 'Oral
glucose tolerance test' - A measurement of blood glucose in the fasting
state and at specific intervals before and after oral or intravenous
glucose load to determine the ability to maintain homeostasis of
glucose.

These terms could be stored with the patient data (in the same database,
or even the same model in the worst-case). However, this would encourage
an extreme amount of redundancy, since there may be thousands of
patients in the same database who have the same, or a related,
condition.

Imagine the weird, convoluted SQL query that would be needed to extract
the number of patients with a family history of ASD, from a database
that stored this information in a textfield, that was 5 years old, and
had been used by thousands of practitioners all over the country, each
deciding, based on how many hours had passed since their last meal, the
level of detail they needed to record this information.

When a practitioner who has a busy schedule is using your EHR system and
all they have is a blank form field, you can't predict what they'll type
into it, *if they actually type into it*.

This is bad for a clinical health system that aims to support `Informed
Decisions`, because the only way to aggregate this information for
useful analysis is to parse unstructured text in different ways,
depending on the language that a practitioner used to input data about
the patient during triage, times the number of patients, times the
number of practitioners, times the number of years the EHR has been
live. The result for the developer, data scientist or analyst: a
combinatorial explosion of *technical debt*.

Clearly, we need a system that enables *effective retrieval and reuse of
clinical information, with appropriate levels of detail*.

In order to unlock many of the potential benefits of electronic health
records, we use SNOMED CT to consistently represent clinical
information. Here are the possible benefits of this approach:

#### Enhancing the care of individual patients:

+ Display of appropriate information to enable clinical staff to assess
the condition and needs of patients;

+ Decision support tools that help to guide safe, appropriate and
effective patient care;

+ Communicating, sharing and maintaining information in ways that enable
different members of the health care team to access and use relevant
information collected at different places and times.

#### Enhancing the care of populations of patients:

+ Epidemiology monitoring and reporting;

+ Research into the causes of diseases;

+ Research into the effectiveness of different approaches to disease
management and treatment.

#### Supporting cost-effective delivery of care:

+ Using decision support to minimize the risk of costly errors in
treatment;

+ Reducing duplication of investigation and interventions through
effective access to shared information about the patient;

+ Auditing the delivery of clinical services; with more opportunity to
analyze outliers and exceptions in the pattern of care delivery;

+ Planning future service delivery based on emerging health trends,
perceived priorities and changes in clinical understanding.

Delivering these benefits depends on consistent representation of the
various types of information that are represented in a health record. It
must be possible to represent this information at different levels of
detail and it must be possible to query this information from various
perspectives and at different levels of detail.

To meet these requirements, *electronic health records* need a
well-maintained terminology. *SNOMED CT* addresses these requirements
and additional practical requirements for an implementable, globally
applicable but locally extensible, multilingual solution.

This server is one such implementation.

Each endpoint listed here contains documentation that explains its
purpose, and how to use it.

# Endpoints

## Release Information

To get information on the current release, use `GET` on
`current_release_information` below.

To get information on all the releases, use `GET` on
`historical_release_information` below.

## Concepts

All concepts are listed in the `all_concepts` endpoint, while endpoints
that rely on the concept views are below it. The usage patterns and
roles of these endpoints are documented on their pages.

This includes the following endpoints:


+ `all_metadata_concepts`
+ `all_core_metadata_concepts`
+ `all_foundation_metadata_concepts`
+ `all_refset_concepts`
+ `all_attribute_concepts`
+ `all_reltype_concepts`
+ `all_namespace_concepts`
+ `all_top_level_concepts`
+ `all_module_identifiers`
+ `all_definition_status_identifiers`
+ `all_description_type_identifiers`
+ `all_case_significance_identifiers`
+ `all_characteristic_type_identifiers`
+ `all_modifer_identifiers`
+ `all_identifier_scheme_identifiers`
+ `all_attribute_value_identifiers`
+ `all_reference_set_descriptor_identifiers`



## Descriptions

    """
    api_list_endpoints = [
        ('current_release_information',
         reverse(
             'terminology:current-snomedct-release',
             request=request, format=format)),
        ('historical_release_information',
         reverse('terminology:historical-releases',
                 request=request, format=format)),
        ('all_concepts',
         reverse('terminology:list-concepts',
                 request=request, format=format)),
        ('all_metadata_concepts',
         reverse('terminology:list-metadata-concepts',
                 request=request, format=format)),
        ('all_core_metadata_concepts',
         reverse('terminology:list-core-metadata-concepts',
                 request=request, format=format)),
        ('all_foundation_metadata_concepts',
         reverse('terminology:list-foundation-metadata-concepts',
                 request=request, format=format)),
        ('all_refset_concepts',
         reverse('terminology:list-refset-concepts',
                 request=request, format=format)),
        ('all_attribute_concepts',
         reverse('terminology:list-attribute-concepts',
                 request=request, format=format)),
        ('all_reltype_concepts',
         reverse('terminology:list-reltype-concepts',
                 request=request, format=format)),
        ('all_namespace_concepts',
         reverse('terminology:list-namespace-concepts',
                 request=request, format=format)),
        ('all_top_level_concepts',
         reverse('terminology:list-top-level-concepts',
                 request=request, format=format)),
        ('all_module_identifiers',
         reverse('terminology:list-module-identifiers',
                 request=request, format=format)),
        ('all_definition_status_identifiers',
         reverse('terminology:list-definition-status-identifiers',
                 request=request, format=format)),
        ('all_description_type_identifiers',
         reverse('terminology:list-description-type-identifiers',
                 request=request, format=format)),
        ('all_case_significance_identifiers',
         reverse('terminology:list-case-significance-identifiers',
                 request=request, format=format)),
        ('all_characteristic_type_identifiers',
         reverse('terminology:list-characteristic-type-identifiers',
                 request=request, format=format)),
        ('all_modifer_identifiers',
         reverse('terminology:list-modifer-identifiers',
                 request=request, format=format)),
        ('all_identifier_scheme_identifiers',
         reverse('terminology:list-identifier-scheme-identifiers',
                 request=request, format=format)),
        ('all_attribute_value_identifiers',
         reverse('terminology:list-attribute-value-identifiers',
                 request=request, format=format)),
        ('all_reference_set_descriptor_identifiers',
         reverse('terminology:list-reference-set-descriptor-identifiers',
                 request=request, format=format)),
        ('list_diseases',
         reverse('terminology:list-diseases',
                 request=request, format=format)),
        ('list_symptoms',
         reverse('terminology:list-symptoms',
                 request=request, format=format)),
        ('list_adverse_reactions',
         reverse('terminology:list-adverse-reactions',
                 request=request, format=format)),
        ('list_procedures',
         reverse('terminology:list-procedures',
                 request=request, format=format)),
        ('list_operative_procedures',
         reverse('terminology:list-operative-procedures',
                 request=request, format=format)),
        ('list_diagnostic_procedures',
         reverse('terminology:list-diagnostic-procedures',
                 request=request, format=format)),
        ('list_prescriptions',
         reverse('terminology:list-prescriptions',
                 request=request, format=format)),
        ('list_dispensing_procedures',
         reverse('terminology:list-dispensing-procedures',
                 request=request, format=format)),
        ('list_drug_regimen_procedures',
         reverse('terminology:list-drug-regimen-procedures',
                 request=request, format=format)),
        ('list_patient_history',
         reverse('terminology:list-patient-history',
                 request=request, format=format)),
        ('list_family_history',
         reverse('terminology:list-family-history',
                 request=request, format=format)),
        ('list_examination_findings',
         reverse('terminology:list-examination-findings',
                 request=request, format=format)),
        ('list_vital_signs',
         reverse('terminology:list-vital-signs',
                 request=request, format=format)),
        ('list_evaluation_procedures',
         reverse('terminology:list-evaluation-procedures',
                 request=request, format=format)),
        ('list_diagnostic_investigations',
         reverse('terminology:list-diagnostic-investigations',
                 request=request, format=format)),
        ('list_imaging_referrals',
         reverse('terminology:list-imaging-referrals',
                 request=request, format=format)),
        ('list_investigation_referrals',
         reverse('terminology:list-investigation-referrals',
                 request=request, format=format)),
        ('list_lab_referrals',
         reverse('terminology:list-lab-referrals',
                 request=request, format=format)),
        ('list_physiology_referrals',
         reverse('terminology:list-physiology-referrals',
                 request=request, format=format)),
        ('list_laboratory_procedures',
         reverse('terminology:list-laboratory-procedures',
                 request=request, format=format)),
        ('list_imaging_procedures',
         reverse('terminology:list-imaging-procedures',
                 request=request, format=format)),
        ('list_evaluation_findings',
         reverse('terminology:list-evaluation-findings',
                 request=request, format=format)),
        ('list_imaging_findings',
         reverse('terminology:list-imaging-findings',
                 request=request, format=format)),
        ('list_specimens',
         reverse('terminology:list-specimens',
                 request=request, format=format)),
        ('list_assesment_scales',
         reverse('terminology:list-assesment-scales',
                 request=request, format=format)),
        ('list_chart_procedures',
         reverse('terminology:list-chart-procedures',
                 request=request, format=format)),
        ('list_administrative_procedures',
         reverse('terminology:list-administrative-procedures',
                 request=request, format=format)),
        ('list_administrative_procedures',
         reverse('terminology:list-administrative-procedures',
                 request=request, format=format)),
        ('list_admission_procedures',
         reverse('terminology:list-admission-procedures',
                 request=request, format=format)),
        ('list_discharge_procedures',
         reverse('terminology:list-discharge-procedures',
                 request=request, format=format)),
        ('list_body_structures',
         reverse('terminology:list-body-structures',
                 request=request, format=format)),
        ('list_body_structures',
         reverse('terminology:list-body-structures',
                 request=request, format=format)),
        ('list_organisms',
         reverse('terminology:list-organisms',
                 request=request, format=format)),
        ('list_substances',
         reverse('terminology:list-substances',
                 request=request, format=format)),
        ('list_drugs',
         reverse('terminology:list-drugs',
                 request=request, format=format)),
        ('list_amps',
         reverse('terminology:list-amps',
                 request=request, format=format)),
        ('list_vmps',
         reverse('terminology:list-vmps',
                 request=request, format=format)),
        ('list_vtms',
         reverse('terminology:list-vtms',
                 request=request, format=format)),
        ('list_vmpps',
         reverse('terminology:list-vmpps',
                 request=request, format=format)),
        ('list_ampps',
         reverse('terminology:list-ampps',
                 request=request, format=format)),
        ('all_descriptions', reverse('terminology:list-descriptions',
                                     request=request, format=format)),
        ('all_relationships', reverse('terminology:list-relationships',
                                      request=request, format=format)),
        ('transitive_closure', reverse('terminology:list-transitive-closure',
                                       request=request, format=format)),
        ('adjacency_list', reverse('terminology:adjacency-list',
                                   request=request, format=format))
    ]

    # Easier to enumerate refset list endpoints like this
    for refset_type in iter(REFSET_MODELS):
        api_list_endpoints.append(
            ('all_' + refset_type.lower() + '_refsets',
             reverse(
                 'terminology:list-' +
                 refset_type.lower().replace('_', '-') + '-refset',
                 request=request,
                 format=format)))

    api_list_endpoints = collections.OrderedDict(api_list_endpoints)

    return Response(api_list_endpoints)


@api_view(['GET'])
def current_release_information(request):
    """Returns basic information pertaining to the most recent SNOMED CT
release that is loaded in the application server."""
    current_international_release = releases()[0]
    current_drug_release = releases(release_type='drug_extension')
    current_uk_clinical_extension_release = releases(release_type='clinical_extension')
    current_release_information = current_international_release.copy()
    current_release_information.update(
        {'current_drug_extension_release': current_drug_release,
         'current_uk_clinical_extension_release': current_uk_clinical_extension_release})

    return Response(current_release_information)


@api_view(['GET'])
def historical_release_information(request):
    """Returns a listing of all the SNOMED CT versions that are loaded into
    the server."""
    return Response(releases(release_type='international_release'))


class ListConcepts(GlobalFilterMixin, ListAPIView):
    """SNOMED CT is a clinical terminology, which is to say that it is a
    *deep* repository of medical knowledge. Its scope is defined separately
    for three dimensions:

a. Domain coverage or breadth.
   It tries to cover as many medical terms as have been introduced in
   the literature.

b. Granularity or depth.
   It tries to cover as many nuanced differences between related
   concepts, with the relationships between them. To this end, for many
   concepts in this terminology, there are a number of refinements that
   mean something slightly different, based on variations in medical
   findings.

c. Knowledge representation.

   SNOMED CT attempts to mirror the real-world experience of the
   practice of medicine as closely as possible. For this to work, it
   should represent the state of our collective knowledge in the latest
   findings, techniques, drugs and technologies that have been observed
   in the profession.


   Here are the kinds of things one should expect to see in this
   terminology server:

   + Clinical findings, including disorders

   + Procedures, broadly defined as including all health related
     activities such as history taking, physical examination, testing,
     imaging, surgical procedures, disease-specific training and
     education, counseling, and so forth.

   + Observable entities which, when given a value, provide a specific
     finding or assertion about health related information. Examples
     include the names of lab tests, physical exam tests, dates of
     significant events, and so forth.

   + Anatomy, morphology, and other body structures

   + Chemicals and other substances of relevance to health and health
     care, including generic drug ingredient names, generic drug
     products (virtual medicinal products)

   + Generic physical devices relevant to health care, or to broad
     categories of injury or accident

   + Organisms relevant to health and health care of humans and animals

   * Other etiologies of disease, including external forces, harmful
     events, accidents, genetic abnormalities,

   + Functions and activities.

   + Social contexts relevant to health, including general categories of
     status of employment, education, housing, care provision, family
     relationships, and so forth.

   + Types of clinical records, documents, certificates and other
     records and record components relevant to health care.

   + Staging, scales, classifications, and other miscellaneous health
     information

   + Attributes and values necessary to organize and structure the
     terminology.


## List

   This view shows a list of all concepts available in the current
   release of the Slade360° SNOMED CT Terminology Server

   This is a *short form* of the `Concept` model, eliding all the JSON
   fields due to the potential size of the objects to be retrieved.

   To view the full representation, see the next section below.

## To view a single concept

   Send a `GET` request to `/terminology/concept/id` to see any specific
   concept, by it's SCTID.

### Example: Meningitis (disorder)

   This has `SCTID=7180009`, so we'll send a `GET` to
   `/terminology/concept/7180009`.


   Go ahead and copy that into the browser's URL bar to see what happens.

   Try the same request with the following SCTIDs to get a feel for the
   API's structure.

   + `161478002`

   + `299729001`

## Full-Text Search

   This server supports full-text search through all descriptions of a
   concept, including commonly used acronyms.


   To find a concept by its descriptions, you send a `GET` request to
   `/terminology/concepts?search=<term>`.

### Example: `MI`

   This is the most common acronym for `Myocardial infarction` - a heart
   attack.  Send a `GET` to `/terminology/concepts?search=MI`.

   Try other searches and see what you get. Note the order of
   results. Here are some acronyms and terms you could use to get
   started. They are chosen to show the variety of concepts you can
   expect to see:

   + `COPD`
   + `COPD lung`
   + `calculus`
   + `ASCUS`
   + `ARF`
   + `acute renal failure`
   + `AKA`
   + `dog breed`
   + `pig breed`
   + `oral glucose tolerance test`
   + `transfer rna`
   + `human genome`

   """

    def get_queryset(self):
        queryset = super(ListConcepts, self).get_queryset()
        params = self.request.query_params

        if params.get('search', None):
            queryset = Concept.objects.search(self.request,
                                              queryset,
                                              self.search_fields).order_by('-rank')
        return queryset

    queryset = Concept.objects.all()
    serializer_class = ConceptListSerializer
    filter_backends = (SearchOrderingFilter, JSONFieldFilter)
    ordering = ('id',)
    search_fields = ('@descriptions',)


class ListDirectParents(GlobalFilterMixin, ListAPIView):
    """This shows a list of all the direct parents of a specific SNOMED CT Concept.
    """
    def get_queryset(self):
        concept_id = self.kwargs.get('concept_id')
        params = self.request.query_params

        queryset = Concept.objects.filter(
            id__in=get_concept_relatives('parents', concept_id)
        )

        if params.get('search', None):
            queryset = Concept.objects.search(self.request,
                                              queryset,
                                              self.search_fields).order_by('-rank')
        return queryset

    serializer_class = ConceptListSerializer
    filter_backends = (SearchOrderingFilter, JSONFieldFilter)
    ordering_fields = ('id', '-rank')
    ordering = ('id',)
    search_fields = ('@descriptions',)


class ListDirectChildren(GlobalFilterMixin, ListAPIView):
    """\ This shows a list of all the direct children of a specific SNOMED
    CT Concept.

# Usage Patterns

## Direct Child Relationship

### Endpoint: `terminology/relationships/children/<concept_id>`

Lists the direct children of the concept identified by `concept_id`.

#### Example: Events

This has the endpoint
`/terminology/relationships/children/272379006/`. Send a `GET` request
to this endpoint to see the list of the types of events recorded in
SNOMED CT.

Here are other examples:

+ `/terminology/relationship/children/123037004`
+ `/terminology/relationship/children/404684003`
+ `/terminology/relationship/children/308916002`
+ `/terminology/relationship/children/272379006`
+ `/terminology/relationship/children/363787002`

## Top-Level Concepts

### Endpoint: `/terminology/concepts/top_level`

This is a shortcut endpoint which lists the direct children of the Root
Concept, which divide the SNOMED CT component hierarchy into its
standard parts:

#### 123037004 | body structure |

The |body structure| concept sub-hierarchy holds the concepts that
directly describe body structures, and sets up scaffolding for talking
about body structures: whether a body structure is present, the level of
specificity required to describe the structure, whether the body
structure is acquired or anatomical etc.


#### 404684003 | clinical finding |

This hierarchy contains all clinical findings found in medicine. From
anxiety disorders (109006), miscarriages (127009), normal peripheral
vision (144008) and more, you'll find here any finding that is known to
medicine. Caveat: remember that the UK and US versions of the clinical
terminology are updated every six months, so it'll take that long for
truly new observations to enter the main terminology from the UK and US
release centers.

#### 308916002 | environment or geographical location |

The | Environment or geographical location | hierarchy includes types of
environments as well as named locations such as countries, states, and
regions.  Examples of Environments and geographic locations concepts:
| Canary islands (geographic location) |, | California (geographic
location) |, | Rehabilitation department (environment) |, | Intensive
care unit (environment) |

#### 272379006 | event |

The | Event | hierarchy includes concepts that represent occurrences
(excluding procedures and interventions).  Examples of Event concepts:
| Flood (event) |, | Bioterrorist attack (event) |, | Earthquake (event) |

#### 363787002 | observable entity |

Concepts in this hierarchy can be thought of as representing a question
or procedure which can produce an answer or a result. For instance,
| Left ventricular end-diastolic pressure (observable entity) | could be
interpreted as the question, “What is the left ventricular end diastolic
pressure?” or “What is the measured left ventricular end-diastolic
pressure?”

#### 410607006 | organism |

This hierarchy includes organisms of significance in human and animal
medicine. Organisms are also used in modeling the causes of diseases in
SNOMED CT. They are important for public health reporting of the causes
of notifiable conditions and for use in evidence-based infectious
disease protocols in clinical decision support systems.

Sub-hierarchies of organism include, but are not limited to:

`| Animal (organism) |` , `| Microorganism (organism) |`, `| Kingdom Plantae (organism) |`.

Examples of Organism concepts:

+ `| Streptococcus pyogenes (organism) |`

+ `| Texon cattle breed (organism) |`

+ `| Bacillus anthracis (organism) |`

+ `| Lichen (plant) (organism) |`.

#### 373873005 | pharmaceutical / biologic product |

The | Pharmaceutical / biologic product | hierarchy is separate from the
| Substance | hierarchy. This hierarchy was introduced as a top-level
hierarchy in order to clearly distinguish drug products (products) from
their chemical constituents (substances).

It contains concepts that represent the multiple levels of granularity
required to support a variety of uses cases such as computerized
provider order entry (CPOE), e-prescribing, decision support and
formulary management. The levels of drug products represented in the
International Release include Virtual Medicinal Product (VMP), Virtual
Therapeutic Moiety (VTM), and Product Category. Additionally, US and UK
drug extensions have been developed, which represent Actual Medicinal
Products (AMPs).

*NOTE*: There is code exploring this hierarchy in depth, with a tutorial
 on how to use the transitive closure of the |is a| relationship
 type. You can find it in the endpoint:
 `/terminology/relationships/transitive_closure`.

#### 78621006 | physical force |

The concepts in the `| Physical force |` hierarchy are directed primarily
at representing physical forces that can play a role as mechanisms of
injury.  Examples of Physical force concepts:

+ `| Spontaneous combustion (physical force) |`

+ `| Alternating current (physical force) |`

+ `| Friction (physical force) |`

####  260787004 | physical object |

Concepts in the `| Physical object |` hierarchy include natural and
man-made objects. One use for these concepts is modeling procedures that
use devices (e.g. catheterization ).  Examples of Physical object
concepts:

+ `| Military vehicle (physical object) |`
+ `| Implant, device (physical object) |`
+ `| Artificial kidney, device (physical object) |`
+ `| Latex rubber gloves (physical object) |`
+ `| Book (physical object) |`
+ `| Pressure support ventilator (physical object) |`
+ `| Vena cava filter (physical object) |`

#### 71388002 | procedure |

`| Procedure |` concepts represent activities performed in the provision
of health care.This hierarchy represents a broad variety of activities,
including but not limited to, invasive procedures (e.g. `| Excision of
intracranial artery (procedure) |`), administration of medicines
(e.g. `| Pertussis vaccination (procedure) |`), imaging procedures
(e.g. `| Ultrasonography of breast (procedure) |`), education procedures
(e.g. `| Low salt diet education (procedure) |`), and administrative
procedures (e.g. `| Medical records transfer (procedure) |`).  Examples
of Procedure concepts:

+ `| Removal of urethral catheter (procedure) |`
+ `| Intravenous steroid injection (procedure) |`
+ `| Irrigation of oral wound (procedure) |`
+ `| Appendectomy (procedure) |`

#### 362981000 | qualifier value |

The `| Qualifier value |` hierarchy contains some of the concepts used as
values for SNOMED CT attributes that are not contained elsewhere in
SNOMED CT. Such a code may be used as the value of an attribute in a
defining Relationship in precoordinated definitions, and/or as the value
of an attribute in a qualifier in a postcoordinated expression. However,
the values for attributes are not limited to this hierarchy and are also
found in hierarchies other than `| Qualifier value |`.

For example, the value for the attribute | LATERALITY | in the concept
shown below is taken from the `| Qualifier value |` hierarchy:

• | Left kidney structure | | LATERALITY | | Left | .

However, the value for the attribute | FINDING SITE | in the concept
shown below is taken from the | Body structure | hierarchy, not the |
Qualifier value | hierarchy.

+ | Pneumonia | | FINDING SITE | | Lung structure | .

Examples of Qualifier value concepts:

+  `| Unilateral |`
+  `| Left |`
+  `| Puncture - action |`

#### 419891008 | record artefact |

A `| Record artifact |` is an entity that is created by a person or
persons for the purpose of providing other people with information about
events or states of affairs. In general, a record is virtual, that is,
it is independent of its particular physical instantiation(s), and
consists of its information elements (usually words, phrases and
sentences, but also numbers, graphs, and other information elements). `|
Record artifact |` need not be complete reports or complete
records. They can be parts of larger `| Record artifact |`. For example,
a complete health record is a `| Record artifact |` that also may
contain other `| Record artifact |` in the form of individual documents
or reports, which in turn may contain more finely granular `| Record
artifact |` such as sections and even section headers.

#### 243796009 | situation with explicit context |

Concepts in the `| Situation with explicit context |` hierarchy (given the appropriate
record structure) can be used in a clinical record to represent:

+ Conditions and procedures that have not yet occurred (e.g. `| Endoscopy
  arranged (situation) |`);

+ Conditions and procedures that refer to someone other than the patient
  (e.g. `| Family history: Diabetes mellitus (situation) |`, `| Discussed
  with next of kin (situation) |`);

+ Conditions and procedures that have occurred at some time prior to the
  time of the current entry in the record (e.g. `| History of - aortic
  aneurysm (situation) |`, `| History of - splenectomy (situation) |`).

In each of these examples, clinical context is specified. The second
example, in which someone other than the patient is the focus of the
concept, could be represented in an application or record structure by
combining a header term Family history with the value Diabetes. The
specific context (in this case, family history) would be represented
using the record structure. In this case, the precoordinated
context-dependent concept | Family history: Diabetes mellitus
(situation) | would not be used because the information model has
already captured the family history aspect of the diabetes.  Concepts in
the | Procedure | and | Clinical finding | hierarchy have a default
context of the following:


+ The procedure has actually occurred (versus being planned or canceled)
  or the finding is actually present (versus being ruled out, or
  considered);

+ The procedure or finding being recorded refers to the patient of
  record (versus, for example, a family member);

+ The procedure or finding is occurring now or at a specified time
  (versus some time in the past).


In addition to using the record structure to represent context, there is
sometimes a need to override these defaults and specify a particular
context using the formal logic of the terminology. For that reason,
SNOMED CT has developed a context model to allow users and/or
implementers to specify context using the terminology, without depending
on a particular record structure. The | Situation with explicit context
| hierarchy and various attributes assigned to concepts in this
hierarchy accomplish this.

Examples of Situation with explicit context concepts:

+ `| Family history: Myocardial infarction (situation) |`
+ `| No family history of stroke (situation) |`
+ `| Nasal discharge present (situation) |`
+ `| Suspected epilepsy (situation) |`

#### 48176007 | social context |

The | Social context | hierarchy contains social conditions and
circumstances significant to healthcare. Content includes such areas as
family status, economic status, ethnic and religious heritage, life
style, and occupations.These concepts represent social aspects affecting
patient health and treatment. Some sub-hierarchies of | Social context |
and concepts typical of those sub-hierarchies are shown in the following
examples.  Examples:

+ `| Ethnic group (ethnic group) |`:

    | Afro-Caribbean (ethnic group) | ;

    | Estonians (ethnic group) | .

+ `| Occupation (occupation) |`:

    | Carpenter, general (occupation) | .

    | Bank clerk (occupation) | ;

+ `| Person (person) |`:

    | Employer (person) | ;

    | Boyfriend (person) | ;



#### 123038009 | specimen |

The | Specimen | hierarchy contains concepts representing entities that
are obtained (usually from a patient) for examination or analysis. |
Specimen | concepts can be defined by attributes which specify: the
normal or abnormal body structure from which they are obtained; the
procedure used to collect the specimen; the source from which it was
collected; and the substance of which it is comprised.

Examples of Specimen concepts:

+ `| Specimen from prostate obtained by needle biopsy (specimen) |`
+ `| Urine specimen obtained by clean catch procedure (specimen) |`
+ `| Calculus specimen (specimen) |`
+ `| Cerebroventricular fluid cytologic material (specimen) |`

#### 254291000 | staging and scales |

This hierarchy contains such sub-hierarchies as `| Assessment scales
(assessment scale) |`, which names assessment scales; and `| Tumor
staging (tumor staging) |` , which names tumor staging systems.
Examples of Assessment scales (assessment scale) concepts:

+ | Glasgow coma scale (assessment scale) | ;
+ | Stanford Binet intelligence scale (assessment scale) | .

Examples of Tumor staging (tumor staging) concepts:

+ | International Federation of Gynecology and Obstetrics (FIGO) staging
system of gynecological malignancy (tumor staging) | ;

+ | Dukes staging system (tumor staging) |

#### 105590001 | substance |

The `| Substance |` hierarchy contains concepts that can be used for
recording active chemical constituents of drug products, food and
chemical allergens, adverse reactions, toxicity or poisoning
information, and physicians and nursing orders. Concepts from this
hierarchy represent general substances and chemical constituents of |
Pharmaceutical / biologic product (product) | which are in a separate
hierarchy. However, sub-hierarchies of | Substance | also include but
are not limited to: | Body substance (substance) | (concepts to
represent body substances); | Dietary substance (substance) |; |
Diagnostic substance (substance) |.

Examples of Substance concepts:

+ `| Insulin (substance) |`
+ `| Methane (substance) |`
+ `| Chromatin (substance) |`
+ `| Dental porcelain material (substance) |`
+ `| Albumin (substance) |`
+ `| Endorphin (substance) |`
+ `| Acetaminophen (substance) |`


#### 900000000000441003 | SNOMED CT Model Component |

The concept named | SNOMED CT Model Component |, which is a child of the
root concept | SNOMED CT Concept |, contains the metadata model that
supports each release.

The root concept can be accessed through `/terminology/concept/root`.

    """
    def get_queryset(self):
        concept_id = self.kwargs.get('concept_id')
        params = self.request.query_params

        queryset = Concept.objects.filter(
            id__in=get_concept_relatives('children', concept_id)
        )

        if params.get('search', None):
            queryset = Concept.objects.search(self.request,
                                              queryset,
                                              self.search_fields).order_by('-rank')
        return queryset

    serializer_class = ConceptListSerializer
    filter_backends = (SearchOrderingFilter, JSONFieldFilter)
    ordering_fields = ('id', '-rank')
    ordering = ('id',)
    search_fields = ('@descriptions',)


class ListAncestors(GlobalFilterMixin, ListAPIView):
    """
    This shows a list of all the ancestors of a specific SNOMED CT Concept.
"""
    def get_queryset(self):
        concept_id = self.kwargs.get('concept_id')

        queryset = Concept.objects.filter(
            id__in=get_concept_relatives('ancestors', concept_id)
        )
        return queryset

    serializer_class = ConceptListSerializer
    filter_backends = (OrderingFilter, JSONFieldFilter)
    ordering = ('id',)
    search_fields = ('@descriptions',)


class ListDescendants(GlobalFilterMixin, ListAPIView):
    """This shows a list of all the descendants of a specific SNOMED CT Concept.

# Usage

## Descendants

### Endpoint: `terminology/relationship/descendants/<concept_id>`

Lists the descendants of the concept identified by `concept_id`, through
iterations of the relationship `<descendant_concept_id> | is a |
<concept_id>`.

#### Example: Events

This has the endpoint
`/terminology/relationships/descendants/272379006/`. Send a `GET` request
to this endpoint to see the list of the types of events recorded in
SNOMED CT.


Here are other examples:

## Metadata Concepts

### Endpoint: `GET` `/terminology/concepts/metadata`

This is a shortcut endpoint which lists the descendants of
`900000000000441003 | SNOMED CT Model Component (metadata) |`, which
contains the non-clinical metadata whose only role is to support the
SNOMED release. As SNOMED CT release file formats contain a number of
concept enumerations, it is necessary to define sets of concepts that
represent the allowed values. As well as the enumerated values, other
metadata supporting the extensibility mechanism and the concept model is
required.  The concept | SNOMED CT Model Component (metadata) | is a
subtype of the root concept ( | SNOMED CT Concept |), and contains the
metadata, supporting the release.

## Core metadata concepts ( applicable to core components )

### Endpoint: `GET` `/terminology/concepts/metadata/core

These are subtypes of `| core metadata concept |`
(900000000000442005). This hierarchy contains the model metadata that is
referenced from the core international release file ( concepts,
descriptions, relationships, identifiers ).


## All reference sets and their metadata

### Endpoint: `GET`  `/terminology/concepts/metadata/foundation/`

All reference sets and their metadata are descendants of `| foundation
metadata concept |` (900000000000454005). This is the metadata that
supports the extensibility mechanism - the concepts needed to describe
reference sets or reference set attributes descend from here.  The
various types of reference sets e.g simple reference sets, attribute
value reference sets are described by concepts that fall under this
hierarchy.


## Relationship types
### Endpoint: `GET`  `/terminology/concepts/attributes/`

Defined as `| attribute |` (246061005) concepts, these are linkage
concepts - concepts intended to link two or more other concepts, in
order to express meaning by composition.

## Concept model attributes


## Endpoint: `GET`  `/terminology/concepts/reltypes/`

Descendants of `| concept model attribute |` (410662002).  This is the
supertype of all relationship types other than `| is a |`. These are
linkage concepts that are approved for use ( there is limited or no
guidance for the others ).

## Namespaces

### `GET`  `/terminology/concepts/namespaces/`

These are subtypes of `|370136006|`. One namespace is assigned for each
organization that produces SNOMED content.


## Navigational Concepts

### Endpoint: `GET` `/terminology/concepts/navigational/`

Concepts that are purely navigational in nature ( no semantic
meaning ) are subtypes of `| navigational concept |` ( 363743006).


## Concept enumeration services

These APIs are conveniences - for the developers of editing
front-ends. All endpoints will return lists of concepts.

The concepts that are to be enumerated under these services are
"regular" concepts - just like any other concepts. Creation, update and
retirement will be carried out using the same general purpose APIs that
will be used for other concepts.

#### Listing of `moduleId` enumerations

Descendants of `900000000000443000` can be listed by issuing a `GET` to
`/terminology/module_identifiers/`.

#### Listing of `definitionStatusId` enumerations

Descendants of `900000000000444006` can be listed by issuing a `GET` to
`/terminology/definition_status_identifiers/`.

#### Listing of `descriptionTypeId` enumerations

Descendants of `900000000000446008` can be listed by issuing a `GET` to
`/terminology/description_type_identifiers/`.

#### Listing of `caseSignificanceId` enumerations

Descendants of `900000000000447004` can be listed by issuing a `GET` to
`/terminology/case_significance_identifiers/`.

#### Listing of `characteristicTypeId` enumerations

Descendants of `900000000000449001` can be listed by issuing a `GET` to
`/terminology/characteristic_type_identifiers/`.

#### Listing of `modifierId` enumerations

Descendants of `900000000000450001` can be listed by issuing a `GET` to
`/terminology/modifier_identifiers/`.

#### Listing of `identifierSchemeId` enumerations

Descendants of `900000000000453004` can be listed by issuing a `GET` to
`/terminology/identifier_scheme_identifiers/`.

#### Listing of `attributeValueId` enumerations

Descendants of `900000000000491004` can be listed by issuing a `GET` to
`/terminology/attribute_value_identifiers/`.

#### Listing of `referenceSetDescriptorId` enumerations

Descendants of `900000000000456007` can be listed by issuing a `GET` to
`/terminology/reference_set_descriptor_identifiers/`.

    """
    def get_queryset(self):
        concept_id = self.kwargs.get('concept_id')
        params = self.request.query_params

        queryset = Concept.objects.filter(
            id__in=get_concept_relatives('descendants', concept_id)
        )

        if params.get('search', None):
            queryset = Concept.objects.search(self.request,
                                              queryset,
                                              self.search_fields).order_by('-rank')
        return queryset

    serializer_class = ConceptListSerializer
    filter_backends = (SearchOrderingFilter, JSONFieldFilter)
    ordering = ('id',)
    search_fields = ('@descriptions',)


class GetConcept(GlobalFilterMixin, RetrieveAPIView):
    """
## Individual concept

## Endpoint: `GET` `/terminology/concept/<id>`

### Purpose

+ Get the root concept
    `GET` `/terminology/concept/root/`

"""
    serializer_class = ConceptDetailSerializer
    lookup_field = 'id'
    queryset = Concept.objects.all()


class ListDescriptions(GlobalFilterMixin, ListAPIView):
    """This shows a list of all descriptions available in the current
release of the Slade360° SNOMED CT Terminology Server.


## To view a single description

   Send a `GET` request to `/terminology/description/*id*` to see any
   specific description, by it's ID.

### Example: Heart attack

   This is the one of the synonyms for the concept `22298006 |
   Myocardial infarction |`.

   It has `ID=37443015`, so we'll send a `GET` to
   `/terminology/description/37443015`.

   Go ahead and copy that into the browser's URL bar to see what happens.

   Try the same request with the following description IDs to get a feel
   for the API's structure.

   + `680900014`

   + `37442013`


## By Concept ID

   To view the descriptions referenced by a specific concept id, send a
   `GET` request to `/terminology/descriptions/concept_id/<concept_id>`.

### Example: Meningitis

   This has SCTID `7180009`. To get the full representation, we send a
   `GET` request to
   `/terminology/descriptions/concept_id/7180009?full=true`

   On using this filter: `?full=true`, we get a description's reference
   set memberships, which is a list of language reference sets that the
   description is in.

   Here are other sctids you can use to get a feel for the API's structure:
   + `161478002`
   + `299729001`
   + `138875005`
    """

    queryset = Description.objects.all()
    serializer_class = DescriptionListSerializer
    filter_backends = (OrderingFilter,)
    ordering = ('id',)


class GetDescription(GlobalFilterMixin, RetrieveAPIView):
    """
## Individual description

## Endpoint: `GET` `/terminology/description/<id>`
"""
    serializer_class = DescriptionDetailSerializer
    lookup_field = 'id'
    queryset = Description.objects.all()


class ListDescriptionsForConcept(GlobalFilterMixin, ListAPIView):
    """This endpoint lists descriptions for a concept id, provided by the
`concept_id` kwarg.  The response data includes extra fields not shown
in the current, shortened, representation. To see all the fields, use
the `full=true` query param.

   ## Example: Meningitis

   This has SCTID `7180009`. To get the full representation, we send a
   `GET` request to
   `/terminology/descriptions/concept_id/7180009?full=true`

   On doing this, we get a description's reference set memberships,
   which is a list of language reference sets that the description is
   in.

   Here are other sctids you can use to get a feel for the API's structure:
   + `161478002`
   + `299729001`

   """
    def get_queryset(self):
        concept_id = self.kwargs.get('concept_id')
        instances = Description.objects.filter(concept_id=concept_id)
        return instances

    serializer_class = DescriptionListSerializer
    filter_backends = (OrderingFilter,)
    ordering = ('id',)


class ListRelationships(GlobalFilterMixin, ListAPIView):
    """This shows a list of all relationships available in the current release
of the Slade360° SNOMED CT Terminology Server.

## To view a single relationship

Send a `GET` request to `/terminology/relationship/*id*` to see any
specific relationship, by it's ID.

### Example: SNOMED Clinical Terms version: 20130131 [R] (January 2013 Release)

This is the `preferred term` of one of the synonyms for the SNOMED CT
root concept, that provides basic information for the release published
in January 2013.

It has `ID=237671401000001122`, so we'll send a `GET` to
`/terminology/relationship/237671401000001122`.

Go ahead and copy that into the browser's URL bar to see what happens.

Try the same request with the following description IDs to get a feel
for the API's structure.

   + `237671501000001121`

   + `237671601000001120`

## To view a concept's defining relationships

Send a `GET` request to `terminology/relationships/defining/<concept
sctid>`.

### Example: Congenital valgus deformity

[A condition](https://en.wikipedia.org/wiki/Valgus_deformity) in which a
bone or joint is twisted outward from the center of the body. It has
SCTID `79609003`, so we'll send a `GET` to
`/terminology/relationships/defining/237671401000001122`.

    """

    def get_queryset(self):
        queryset = super(ListRelationships, self).get_queryset()

        destination_id = self.kwargs.get('destination_id')
        source_id = self.kwargs.get('source_id')

        if source_id:
            return queryset.filter(source_id=source_id)
        elif destination_id:
            return queryset.filter(destination_id=destination_id)
        else:
            return queryset

    serializer_class = RelationshipSerializer
    filter_backends = (OrderingFilter,)
    ordering = ('id',)
    queryset = Relationship.objects.all()


class ListDefiningRelationships(GlobalFilterMixin, ListAPIView):
    """##Lists the defining relationships for a concept.

These are the concepts that express what is known to be true of a
concept. This may include all the separate things that a concept is,
what it is a part of and how it relates to other concepts.

A defining relationship is one for which the value of the field
`characteristic_type_id` is a descendant of `900000000000006009
|Defining relationship (core metadata concept)|`.

In the current version, that is `900000000000011006 |Inferred relationship|`.

### Example: | Myocardial infarction | 22298006

#### Endpoint: /terminology/relationships/defining/22298006/

Notice that the defining concepts of | Myocardial infarction | are |
Myocardial disease |, | Infarct |

    """

    def get_queryset(self):
        queryset = super(ListDefiningRelationships, self).get_queryset()

        concept_id = self.kwargs.get('concept_id')
        defining_relationships = queryset.filter(
            source_id=concept_id,
            characteristic_type_id=900000000000011006)
        return defining_relationships

    queryset = Relationship.objects.all()
    serializer_class = RelationshipSerializer
    filter_backends = (OrderingFilter,)
    ordering = ('id',)


class ListAllowableQualifiers(GlobalFilterMixin, ListAPIView):
    """##Lists the allowable qualifying relationships for a concept.

A qualifying relationship is not part of the definition of the concept,
but is used to convey some additional information about the
concept. This additional information may only be applicable to a
particular jurisdiction or use case.
   """

    def get_queryset(self):
        concept_id = self.kwargs.get('concept_id')
        qualifier_value_sctid = 362981000
        qualifying_relationships = Relationship.objects.filter(
            source_id=concept_id,
            destination_id__in=get_concept_relatives('descendants', qualifier_value_sctid)
        )
        return qualifying_relationships

    serializer_class = RelationshipSerializer
    filter_backends = (OrderingFilter,)
    ordering = ('id',)


@api_view(['GET'])
def get_relationship(request, id):
    active = request.query_params.get('active', True)

    try:
        instance = Relationship.objects.get(id=id, active=as_bool(active))
    except Relationship.DoesNotExist:
        raise APIException(detail="Relationship matching query does not exist")

    serializer = RelationshipSerializer(instance,
                                        context={'request': request})
    return Response(serializer.data)


class TransitiveClosureList(GlobalFilterMixin, ListAPIView):
    """# Purpose

This endpoint lists all of the `| is a |` relationships in the SNOMED CT
concept hierarchy.

# Usage Patterns

## Children

### Endpoint: `GET` `/terminology/relationships/transitive_closure_descendants/<supertype_id>` #noqa

This endpoint will list, in short form the `SCTID`s associated with
concepts that are subtypes of the given `supertype_id`, which is itself
a `SCTID`.

## Parents

### Endpoint: `GET` `/terminology/relationships/transitive_closure_ancestors/<subtype_id>` #noqa

This endpoint will list, in short form the `SCTID`s associated with
concepts that are supertypes of the given `subtype_id`, which is a `SCTID`.

## Reading this data in file form, as an adjacency list (for Graph Toolkits like `networkx`)

### Endpoint: `GET` `/terminology/relationships/transitive_closure/adjacency_list` #noqa

This endpoint serves a file in plain-text format, structured in the
adjacency list format required to read data into a graph toolkit like
networkx.

Here is sample code to load the data into a graph and test its
correctness, and parse the SNOMED Directed Graph for drugs in the
five-box DM+D hierarchy.


# The SNOMED Graph
## Reading Format

The SNOMED Graph is designed as a Directed Acyclic Graph, with a single
root node called the Root Concept, or `SNOMED CT Concept (SNOMED
RT+CTV3) |138875005|`. Each concept in SNOMED is connected to one or
more concepts through various types of relationships, such as `|Is a|`,
`|Part of|`, `|Has AMP|` etc. as you'll see later on in this
notebook. Due to its size, importance, and the computational difficulty
of generating it, the `|Is a|` relationship subgraph (list of all `Is a`
relationship pairs of the form `A |is a| B`) is denormalized to a format
called the [`transitive
closure`](https://en.wikipedia.org/wiki/Transitive_closure#In_graph_theory)
of the `|Is a|` relationship subgraph. For example, if we have this
relationship structure:

+ ```A |is a| B```
+ ```B |is a| C```
+ ```C |is a| D```

Then the transitive closure will look like this:

*`[(A,B),(A,C),(A,D),(B,C),(B,D),(C,D)]`*.

This data structure easily answers the question: `can I reach D from A
by asking whether I can reach B from A, then asking whether I can reach
C from B?`. If there's a tuple `(A,D)`, then the answer is yes. If the
tuple doesn't exist, then the answer is No.

This example graph, with three simple relationships, spawns a transitive
closure with six connections. The SNOMED transitive closure has
15,592,960 connections between 903,389 concepts.

In order to do anything relevant with SNOMED, such as collecting a list
of drugs in the DM+D hierarchy (see below), we need this structure
because it enables quick and efficient discovery of the local 'friends'
of any given concept.

To make it easier to download this data structure, we precomputed this
transitive closure as an [adjacency list (click here if you don't know
what that
is)](networkx.readthedocs.io/en/latest/reference/readwrite.adjlist.html)
using the parent-child relationship, and stored it in a file that can be
easily downloaded from the terminology server API. [This link points to
the
file](http://snomedct-terminology-server-2016-07-04.slade360emr.com/terminology/relationships/transitive_closure/adjacency_list),  # noqa
and will automatically start a download if you click on it.

In the two cells below, we've downloaded the adjacency list using
`requests`, and saved it to a file
`transitive_closure_adjacency_list.adjlist`. The file extension
`.adjlist` is just plain text, so there's no extra processing required.

    import requests
    response=requests.get(
        "http://snomedct-terminology-server-2016-07-04.slade360emr.com/terminology/relationships/transitive_closure/adjacency_list"  # noqa
    )

    with open('transitive_closure_adjacency_list.adjlist', 'w') as f:
      f.write(response.text)


    # Start here if you don't want to download the adjacency list again.


    import re
    import requests
    from itertools import chain
    import networkx as nx
    from simplejson import loads, load,dumps,dump
    from requests.packages.urllib3.util.retry import Retry
    from requests.adapters import HTTPAdapter

    # Initialize an empty directed graph (digraph) and use
    # read_adjlist to read the downloaded file using the empty digraph.

    G=nx.DiGraph()
    DG = nx.read_adjlist('transitive_closure_adjacency_list.adjlist', create_using=G)

    # The number of nodes in the graph should be equal to the number of
    # concepts in the current release of SNOMED.

    DG.number_of_nodes()

    ### Child concepts of 'Actual medicinal product'. These are the
    ### Actual Medicinal Products in our drug hierarchy


    amp_successors = DG.successors('10363901000001102')

    ### DM+D Hierarchy identifiers - SCTIDs of AMP,AMPP,VMP,VTM,VMPP


    amp=10363901000001102
    vmpp=8653601000001108
    vmp=10363801000001108
    vtm=10363701000001104
    ampp=10364001000001104
    dmd_hierarchy_identifiers = ['10363901000001102',
                                 '8653601000001108',
                                 '10363801000001108',
                                 '10363701000001104',
                                 '10364001000001104']


    ### Obtain the SCTIDs for the children of "9191801000001103 |Trade family (product)|", which aren't needed here  # noqa

    trade_family = DG.successors('9191801000001103')

    #### example using | Zinnat 125mg tablets (GlaxoSmithKline) (product) | 228011000001102
    #### get the 3 direct parents of "228011000001102 |Zinnat 125mg tablets (GlaxoSmithKline) (product)|"  # noqa

    zinnat_predecessors=DG.predecessors('228011000001102')

    non_trade_zinnat_predecessors = [x for x in zinnat_predecessors if x not in trade_family]

    non_dmd_predecessors_of_zinnat = [x for x in non_trade_zinnat_predecessors if x not in dimension_1_dmd_hierarchy_identifiers]  # noqa

    # returns the only parent of zinnat in the drug hierarchy
    non_dmd_predecessors_of_zinnat

    #### The amp-vmp map is correct once we remove trade family hierarchy and dmd hierarchy identifiers from the predecessors list  # noqa
    We map each amp with its corresponding vmp parent. We get a list of dicts with the format:

    `[{'amp': <amp>, 'corresponding_vmp': <vmp>}, ...]`


    amp_drugs_and_their_vmp_parents = []
    for amp_drug in amp_successors:
        parents_of_amp = DG.predecessors(amp_drug)
        for parent_of_amp in parents_of_amp:
            if not  parent_of_amp in trade_family and not parent_of_amp in dmd_hierarchy_identifiers:
                amp_drugs_and_their_vmp_parents.append({'amp': amp_drug, 'corresponding_vmp': parent_of_amp})  # noqa

    print(len(amp_drugs_and_their_vmp_parents))
    print(amp_drugs_and_their_vmp_parents[0])

    # The SCTID of the | Parmaceutical / biologic Product | concept
    pharma_sctid=373873005
    # Get the children of "Virtual Medicinal Product"
    vmp_successors = DG.successors(str(vmp))
    # get the children of "Virtual Therapeutic Moiety"
    vtm_successors = DG.successors(str(vtm))
    # get the children of "Pharmaceutical / biologic Product"
    pharma_successors = DG.successors(str(pharma_sctid))
    # get the descendants of "Pharmaceutical / biologic Product"
    pharma_descendants = nx.descendants(DG, str(pharma_sctid))

    # Connect each amp-vmp map with its corresponding 'virtual therapeutic moiety'
    # by getting each ancestor of the drug code in 'corresponding_vmp' and
    vtms = []
    for amp_vmp_map in amp_drugs_and_their_vmp_parents:
        ancestors_of_vmp = nx.ancestors(DG, amp_vmp_map['corresponding_vmp'])
        for ancestor in ancestors_of_vmp:
            if ancestor in vtm_successors and not ancestor in dmd_hierarchy_identifiers:
                vtms.append({'amp': amp_vmp_map['amp'], 'vmp': amp_vmp_map['corresponding_vmp'], 'vtm': ancestor})
    full_dmd = []

    for amp_vmp_vtm_map in vtms:
        ancestors_of_vtm = nx.ancestors(DG, amp_vmp_vtm_map['vtm'])
        for ancestor in ancestors_of_vtm:
            if ancestor in pharma_successors:
                full_dmd.append({'amp': amp_vmp_vtm_map['amp'],
                                 'vmp': amp_vmp_vtm_map['vmp'],
                                 'vtm': amp_vmp_vtm_map['vtm'],
                                 'drug_class': ancestor})

    full_dmd_with_class_hops = []

    for amp_vmp_vtm_map in vtms[:]:
        ancestors_of_vtm = nx.ancestors(DG, amp_vmp_vtm_map['vtm'])
        non_dmd_vtm_ancestors = set(ancestors_of_vtm).intersection(pharma_descendants)
        for ancestor in ancestors_of_vtm:
            if ancestor not in pharma_successors and not in
            if ancestor in pharma_successors:
                 full_dmd_with_class_hops.append({'amp': amp_vmp_vtm_map['amp'],
                                 'vmp': amp_vmp_vtm_map['vmp'],
                                 'vtm': amp_vmp_vtm_map['vtm'],
                                 'drug_class': ancestor})


    concept_by_id_list_api = "http://snomedct-terminology-server-2016-07-04.slade360emr.com/terminology/concept_list_by_id/"

    Takes a list of valid SCTIDs and returns a dict mapping
    {'<sctid>': <preferred_term>, '<sctid>': <preferred_term>, ...}

    def get_concept_term_by_id_list(id_list):
        ids = ','.join(id_list)
        try:
            response = requests.post(concept_by_id_list_api,data={'sctid_list': ids}).text
        except Exception as e:
            print("Request failed at id {}. Retrying...".format(id_list))
            return get_concept_term_by_id_list(id_list)
        try:
            data = loads(response)
        except Exception as e:
            print(response)
        return data

    # test the function by confirming these values
    get_concept_term_by_id_list([val for val in full_dmd[0].values()])


    # extract all of the ids from the dict, into a list,
    # then get their preferred terms from the SNOMED CT Termserver API
    dmd_values = [list(obj.values()) for obj in full_dmd]
    dmd_id_set=set(list(chain(chain(*dmd_values))))
    print("number of sctids in this hierarchy: {}".format(len(dmd_id_set)))
    dmd_name_data=get_concept_term_by_id_list(list(dmd_id_set))


    dmd_data_flattened = []
    for dmd_datum in full_dmd:
        dmd_data_flattened.append(
        {'drug_class': dmd_name_data[dmd_datum['drug_class']] + ' | {}'.format(dmd_datum['drug_class']),
         'amp' : dmd_name_data[dmd_datum['amp']]  + ' | {}'.format(dmd_datum['amp']),
         'vmp': dmd_name_data[dmd_datum['vmp']] + ' | {}'.format(dmd_datum['vmp']),
         'vtm': dmd_name_data[dmd_datum['vtm']] + ' | {}'.format(dmd_datum['vtm'])
         })

    # check consistency of the flattened dm+d data,
    # by confirming that the sctid concatenated with the pipe is correct for the preferred term,
    # for any given row
    dmd_data_flattened[0]

    columns_map = map(lambda x: x.keys(), dmd_data_flattened)
    columns_list = chain.from_iterable([list(list(column)) for column in columns_map])
    columns=list(set(list(columns_list)))

    # Confirm whether a given row has the correct structure.
    # If the results of line 2 match (by column) those of line 1, we're good
    print(columns)
    list(map(lambda x: dmd_data_flattened[0].get(x,""),columns))

    # write data to csv file
    import csv
    with open('dmd_data_full.csv', 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(columns)
        for input_row in dmd_data_flattened:
            csv_writer.writerow(list(map(lambda x: input_row.get(x,""),columns)))

    """

    queryset = TransitiveClosure.objects.all()
    serializer_class = TransitiveClosureSerializer
    filter_backends = (OrderingFilter,)
    ordering = ('supertype_id', 'subtype_id')


@api_view(['GET'])
def transitive_closure_ancestors(request, subtype_id):
    instances = TransitiveClosure.objects.filter(subtype_id=subtype_id)
    serializer = TransitiveClosureSerializer(instances,
                                             many=True,
                                             context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def transitive_closure_descendants(request, supertype_id):
    instances = TransitiveClosure.objects.filter(supertype_id=supertype_id)
    serializer = TransitiveClosureSerializer(instances,
                                             many=True,
                                             context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_adjacency_list(request):
    adjacency_list_file = os.getenv('ADJACENCY_LIST_FILE', '')

    file_name = adjacency_list_file.split('/')[-1]

    with open(adjacency_list_file) as f:
        response = HttpResponse(FileWrapper(f), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            file_name)
        return response


@api_view(['GET'])
def get_relationship_destination_by_type_id(request, type_id):
    """Uses the `type_id` param to get either of two resources as json objects:

1. `Has VMP`: Get a mapping of `{'id': 'destination_id'}` for each concept\
 whose outgoing relationships include one whose `type_name` is 'Has VMP'.
This is a list of all Virtual Medicinal Product Packs, connected to their \
Virtual Medicinal Product parents.

2. `Has AMP`: Get a mapping of `{'id': 'destination_id'}` for each concept\
 whose outgoing relationships include one whose `type_name` is 'Has AMP'.
This is a list of all Actual Medicinal Product Packs, connected to their \
Actual Medicinal Product parents.

The queries to get these are rather slow, so we've cached them in two \
materialized views `has_vmp_destination_ids` and `has_amp_destination_ids`.\
The `type_id` param now only helps us decide which materialized view to query."""

    has_vmp_relationship_type_id = 10362601000001103
    has_amp_relationship_type_id = 10362701000001108
    has_dose_form_relationship_type_id = 411116001
    requested_id = int(type_id)
    amp_query = "select * from has_amp_destination_ids"
    vmp_query = "select * from has_vmp_destination_ids"
    dose_form_query = "select * from has_dose_form_destination_ids"

    if requested_id == has_vmp_relationship_type_id:
        return Response(execute_query(vmp_query))
    elif requested_id == has_amp_relationship_type_id:
        return Response(execute_query(amp_query))
    elif requested_id == has_dose_form_relationship_type_id:
        return Response(execute_query(dose_form_query))
    else:
        raise APIException(
            detail="""Please use one of '10362601000001103' or\
'10362701000001108' as the param to this endpoint. You used: {}""".format(type_id))


@api_view(['POST'])
def get_concept_list_by_id(request):
    """This view only supports POST requests using a JSON object with a
single key: `sctid_list`, whose value is a list of integers. All
integers in `sctid_list` must be valid SNOMED CT identifiers, so that
from this list, we get a JSON object of the form:

      {'<sctid>':<preferred_term>, '<sctid>':<preferred_term>, ...}

 The query used is designed to be as efficient as possible, since the
`sctid_list` might be very large, as is the case when an ETL client is
trying to get the preferred terms for 100,000+ concept ids at once.

A one-by-one strategy where we send `GET` requests for each concept's
preferred term that we need simply won't work since the time to get a single
concept's preferred term is typically ~0.448 ms. Multiplied by 100,000, and it
takes 448s (slightly less than 8 minutes) for all concepts. This is
problematic, so we use a `POST` request (with a high request size limit on our
 webserver) to gather all concept ids that we need.

See [PostgreSQL's JSON functions
documentation](https://www.postgresql.org/docs/current/static/functions-json.html)
for an explanation of the json functions used, and [PostgreSQL's
aggregate functions
documentation](https://www.postgresql.org/docs/9.5/static/functions-aggregate.html)
for an explanation of the `array_agg` function used here.

    """
    ids = request.data.get('sctid_list')
    query = """
SELECT json_object(array_agg(id::text), array_agg(preferred_term))
    FROM snomed_denormalized_concept_view_for_current_snapshot WHERE id IN %s"""
    if ids:
        tuple_of_ids = tuple(ids.split(','))
        concept_preferred_terms = execute_query(query, tuple_of_ids)
        return Response(concept_preferred_terms)
    else:
        raise APIException(
            detail="Please provide a list of sctids. You sent: {}".format(request.data))
