# include historical relationships?
# expression subsumption testing (validation) through set intersection?

from unittest import TestCase
from expressions.tools import execute_expression, validate_expression, ExpressionSyntaxError
from snomedct_terminology_server.server.utils import execute_query
from snomedct_terminology_server.server.models import Concept

class TestExpressionExecutor(TestCase):
    def test_simple_expression(self):
        diabetes_mellitus = {
            "id": 73211009,
            "effective_time": "2002-01-31",
            "active": true,
            "module_id": 900000000000207008,
            "module_name": "SNOMED CT core module (core metadata concept)",
            "definition_status_id": 900000000000074008,
            "definition_status_name": "Primitive",
            "is_primitive": true,
            "fully_specified_name": "Diabetes mellitus (disorder)",
            "preferred_term": "Diabetes mellitus (disorder)",
            "definition": []
        }

        assert execute_expression("73211009") == diabetes_mellitus

        with self.assertRaises(ExpressionSyntaxError):
            execute_expression("7321")

        with self.assertRaises(ExpressionSyntaxError):
            execute_expression("73211009 |")

    def test_expression_sctid_validity(self):
        focus_concepts = "421720008 |spray dose form| + 7946007 |drug suspension|"
        assert validate_expression(focus_concepts).sctid_list == ['421720008', '7946007']
        queryset = Concept.objects.filter(id__in=['421720008', '7946007'])
        assert len(queryset) == 2

class TestAttributes(TestCase):
    def test_clinical_finding_attributes_allowable_values(self):
        """The operators:

        '==' means 'this specific concept'

        '<<' means descendants and self of

        '<=' means descendants only (stated) except for supercategory
        groupers (sufficiently defined by reference to a value that is
        at the top of the value hierarchy)

        '<< Q' means descendants and self of the attribute value,
        including qualifying relationships.

        '<< Q only' means descendants and self of the attribute value,
        but only through qualifying relationships

        """

        finding_site_attribute_template = "363698007 | finding site | = {attribute_value}"
        attribute_value = 'some concept'
        # | Anatomical or acquired body structure | 442083009 (<<)
        assert attribute_value in descendants_and_self_of('442083009')

    def test_allowable_defining_attributes_for_hierarchy(self):
        """
        {
            '123037004': 'Body structure',
            '123038009': 'Material (structure, substance, device) removed from a source (patient, donor, physical location, product)',
            '243796009': 'Situation with explicit context',
            '260787004': 'Physical object (physical object)',
            '272379006': 'Events (event)',
            '373873005': 'Pharmaceutical / biologic product',
            '404684003': 'Clinical finding',
            '71388002': 'Procedure'
        }
"""
        allowable_attributes_map = {
            "123037004" : ['|Laterality|'],

            "404684003" : ['| After |',
                           '| Associated morphology |',
                           '| Associated with |',
                           '| Causative agent |',
                           '| Clinical course |',
                           '| Due to |',
                           '| Episodicity |',
                           '| Finding informer |',
                           '| Finding method |',
                           '| Finding site |',
                           '| Has definitional manifestation |',
                           '| Has interpretation |',
                           '| Interprets |',
                           '| Occurrence |',
                           '| Pathological process |',
                           '| Severity |'],

            "243796009" : ['| Associated finding |',
                           '| Associated procedure |',
                           '| Finding context |',
                           '| Procedure context |',
                           '| Subject relationship context |',
                           '| Temporal context |'],

            "272379006" : ['| After |'
                           '| Associated with |',
                           '| Causative agent |',
                           '| Due to |',
                           '| Occurrence |'],

            "373873005" : ['| Has active ingredient |',
                           '| Has dose form |'],

            "260787004" : ['| Has active ingredient |',
                           '| Has dose form |'],

            "71388002" : ['| Access |',
                          '| Component |',
                          '| Direct device |',
                          '| Direct morphology |',
                          '| Direct substance |',
                          '| Has focus |',
                          '| Has intent |',
                          '| Has specimen |',
                          '| Indirect device |',
                          '| Indirect morphology |',
                          '| Measurement method |',
                          '| Method |',
                          '| Priority |',
                          '| Procedure device |',
                          '| Procedure morphology |',
                          '| Procedure site |',
                          '| Procedure site - Direct |',
                          '| Procedure site - Indirect |',
                          '| Property |',
                          '| Recipient category |',
                          '| Revision status |',
                          '| Route of administration |',
                          '| Scale type |',
                          '| Surgical Approach |',
                          '| Time aspect |',
                          '| Using device |',
                          '| Using access device |',
                          '| Using energy |',
                          '| Using substance |'],

            "123038009" : ['| Specimen procedure |',
                           '| Specimen source identity |',
                           '| Specimen source morphology |',
                           '| Specimen source topography |',
                           '| Specimen substance | '],
        }


    def test_allowed_attributes_by_domain(self):
        # keys
        allowed_attributes_by_domain = {
            "433590000" : [
                '| Route of administration |'
            ],

            "91723000" : [
                '| Laterality |',
                '| Part of |'],

            "404684003" : [
                '| After |',
                '| Associated morphology |',
                '| Associated with |',
                '| Causative agent |',
                '| Clinical course |',
                '| Due to |',
                '| Episodicity |',
                '| Finding informer |',
                '| Finding method |',
                '| Finding site |',
                '| Has interpretation |',
                '| Interprets |',
                '| Laterality |', # only in close-to-user form
                '| Occurrence |',
                '| Pathological process |',
                '| Severity |'],

            "Disorder (finding)" : [
                "| Has definitional manifestation |"
            ],

            "Drug delivery device (physical object)" : [
                "| Has active ingredient |",
                "| Has dose form |"],

            "386053000 | Evaluation procedure (procedure) |" : [
                "| Component |",
                "| Has specimen |",
                "| Measurement method |",
                "| Property |",
                "| Scale type |",
                "| Time aspect |"],

            "272379006 |Event (event) |" : [
                "| After |",
                "| Associated with |",
                "| Causative agent |",
                "| Due to |",
                "| Occurrence |"],

            "71388002 | Procedure (procedure)|" : [
                "| Access |",
                "| Direct device |",
                "| Direct morphology |",
                "| Direct substance |",
                "| Has focus |",
                "| Has intent |",
                "| Indirect device |",
                "| Indirect morphology |",
                "| Method |",
                "| Priority |",
                "| Procedure device |",
                "| Procedure morphology |",
                "| Procedure site |",
                "| Procedure site - Direct |",
                "| Procedure site - Indirect |",
                "| Recipient category |",
                "| Revision status |",
                "| Using device |",
                "| Using access device |",
                "| Using energy |",
                "| Using substance |"],

            "243796009 | Situation with explicit context (situation)| " : [
                "| Subject relationship context |",
                "| Temporal context |"],

            "Finding with explicit context (situation) - descendants only" : [
                "| Associated finding |"
            ], # < 413350009 : 246090004 = (< 404684003 | Clinical finding (<=)(< Q) | OR < 272379006 | Event (<=)(< Q) | OR < 363787002 | Observable entity (< Q only) | OR < 416698001 | Link assertion  (< Q only) | OR  < 71388002 | Procedure (< Q only) |)

            "Finding with explicit context (situation) - self and descendants" : [
                "| Finding context |"
            ], # << 413350009 | Finding with explicit context (situation) |: 408729009 | finding context | = 410514004 | Finding context value (<=)(< Q) |

            "Procedure with explicit context (situation) - descendants only" : [
                "| Associated procedure |"
            ], # < 129125009 : 363589002 | associated procedure | = (< 71388002 | Procedure  (<=)(< Q) | OR  < 363787002 | Observable entity  (< Q only) | )

            "Procedure with explicit context (situation) - self and descendants" : [
                "| Procedure context |"
            ], # << 129125009 | Procedure with explicit context (situation) | : 408730004 | procedure context | = <  288532009 | Context values for actions  (<=)(< Q) |

            "123038009 | Specimen (specimen) |" : [ # 123038009 :
                "| Specimen procedure |",  # 118171006 | specimen procedure | = < 71388002
                "| Specimen source identity |", # 118170007 | specimen source identity | = ( << 125676002 | Person | OR << 35359004 | Family | OR << 133928008 | Community | OR << 49062001 | Device | OR << 276339004 | Environment |
                "| Specimen source morphology |", # 118168003 | specimen source morphology | = << 49755003 | Morphologically abnormal structure |
                "| Specimen source topography |", # 118169006 | specimen source topography | = << 442083009 | Anatomical or acquired body structure |
                "| Specimen substance |" # 370133003 | specimen substance | = << 105590001 | Substance |
            ],

            "387713003 | Surgical procedure (procedure) |" : [
                "| Surgical Approach |" # 424876005 | surgical approach | = < 103379005 | Procedural approach <= |
            ]
        }

        # descendants_of(sctid, exclude_supercategory_groupers=False, qualifiers=None)
        # assert qualifiers in ('only', 'include', None)

        # descendants_and_self_of(sctid)

    def test_attribute_allowable_ranges(self):
        # | ACCESS | -> | Surgical access values | 309795001 (<=)(< Q)
        access_attribute_template = "260507000 | access | = {attribute_value}"

        # | ASSOCIATED FINDING | -> | Clinical finding | 404684003 (<=)(< Q)
        #                        -> | Event | 272379006 (<=)(< Q)
        #                        -> | Observable entity | 363787002 (< Q only)
        #                        -> | Link assertion | 416698001 (< Q only)
        #                        -> | Procedure | 71388002 (< Q only)
        associated_finding_attribute_template = "246090004 | associated finding | = {attribute_value}"

        # | ASSOCIATED PROCEDURE | -> | Procedure | 71388002 (<=)(< Q)
        #                          -> | Observable entity | 363787002 (< Q only)
        associated_procedure_attribute_template = "363589002 | associated procedure | = {attribute_value}"

        # | Morphologically abnormal structure | 49755003 (<<)
        associated_morphology_attribute_template = "116676008 | associated morphology | = {attribute_value}"

        # | Clinical Finding | 404684003 (<<)
        # | Procedure | 71388002 (<<)
        # | Event | 272379006 (<<)
        # | Organism | 410607006 (<<)
        # | Substance | 105590001 (<<)
        # | Physical object | 260787004 (<<)
        # | Physical force | 78621006 (<<)
        # | Pharmaceutical / biologic product | 373873005 (<< Q only)
        # | SNOMED CT Concept | 138875005 (==)
        associated_with_attribute_template = "47429007 | associated with | = {attribute_value}"

        # | Organism | 410607006 (<<)
        # | Substance | 105590001 (<<)
        # | Physical object | 260787004 (<<)
        # | Physical force | 78621006 (<<)
        # | Pharmaceutical / biologic product | 373873005 (<< Q only)
        # | SNOMED CT Concept | 138875005 (==)
        causative_agent_attribute_template = "246075003 | causative agent | = {attribute_value}"


        # | COMPONENT | -> | Substance | 105590001 (<=)(< Q)
        #               -> | Observable entity | 363787002 (<=)(< Q)
        #               -> | Cell structure | 4421005 (<=)(< Q)
        #               -> | Organism | 410607006 (<=)(< Q)
        component_attribute_template = "246093002 | component | = {attribute_value}"


        # | DIRECT DEVICE | -> | Device | 49062001 (<<)
        direct_device_attribute_template = "363699004 | direct device | = {attribute_value}"


        # | DIRECT MORPHOLOGY | -> | Morphologically abnormal structure | 49755003 (<<)
        direct_morphology_attribute_template = "363700003 | direct morphology | = {attribute_value}"


        # | DIRECT SUBSTANCE | -> | Substance | 105590001 (<<)
        #                      -> | Pharmaceutical / biologic product | 373873005 (<<)
        direct_substance_attribute_template = "363701004 | direct substance | = {attribute_value}"

        # | Clinical Finding | 404684003 (<=)
        # | Event | 272379006 (<=)
        due_to_attribute_template = "42752001 | due to | = {attribute_value}"

        # | Clinical Finding | 4046840 (<<)
        # | Procedure | 71388002 (<<)
        after_attribute_template = "255234002 | after | = {attribute_value}"

        # | Severities | 272141005 (<=)(< Q)
        severity_attribute_template = "246112005 | severity | = {attribute_value}"

        # | Courses | 288524001 (<=)(< Q)
        clinical_course_template = "263502005 |clinical course| = {attribute_value}"

        # For example, asthma with | EPISODICITY |=| first episode |
        # represents the first time the patient presents to their health
        # care provider with asthma. EPISODICITY is not used to model
        # any concepts precoordinated in the International Release but
        # it can still be used in postcoordination as a qualifier.

        # | Episodicities | 288526004 (<=)(< Q)
        episodicities_template = "246456000 |episodicity| = {attribute_value}"

        # | Observable entity | 363787002 (<<)
        # | Laboratory procedure | 108252007 (<<)
        # | Evaluation procedure | 386053000 (<<)
        interprets_template = "363714003 |interprets| = {attribute_value}"

        # | Findings values | 260245000 (<<)
        has_interpretation_template = "363713009 | has interpretation| = {attribute_value}"

        # | Autoimmune | 263680009 (==)
        # | Infectious process | 441862004 (<<)
        # | Hypersensitivity process | 472963003 (< <)
        pathological_process_template = "370135005 | pathological process| = {attribute_value}"

        # | Clinical finding | 404684003 (<<)
        has_definitional_manifestation_template = "363705008 |has definitional manifestation| = {attribute_value}"

        # | Periods of life | 282032007 (<)
        occurrence_template = "246454002 |occurrence| = {attribute_value}"

        # | Procedure | 71388002 (<=)
        finding_method_template = "418775008 |finding method| = {attribute_value}"

        # | Performer of method | 420158005 (<<)
        # | Subject of record or other provider of history | 419358007 (<<)
        finding_informer_template = "419066007 |finding informer| = {attribute_value}"

        # | HAS DOSE FORM | -> | Type of drug preparation | 105904009 (<<)
        has_dose_form_attribute_template = "411116001 | has dose form | = {attribute_value}"

        # | HAS ACTIVE INGREDIENT | -> | Substance | 105590001 (<<)
        has_active_ingredient_attribute_template = "127489000 | has active ingredient | = {attribute_value}"


        # | HAS FOCUS | -> | Clinical finding | 404684003 (<<)
        #               -> | Procedure | 71388002 (<<)
        has_focus_attribute_template = "363702006 | has focus | = {attribute_value}"


        # | HAS INTENT | -> | Intents (nature of procedure values) | 363675004 (<=)
        has_intent_attribute_template = "363703001 | has intent | {attribute_value}"

        # | HAS SPECIMEN | -> | Specimen | 123038009 (<=)(< Q)
        has_specimen_attribute_template = "116686009 | has specimen | = {attribute_value}"


        # | INDIRECT DEVICE | -> | Device | 49062001 (<<)
        indirect_device_attribute_template = "363710007 | indirect device | = {attribute_value}"


        # | INDIRECT MORPHOLOGY | -> | Morphologically abnormal structure | 49755003 (<<)
        indirect_morphology_attribute_template = "363709002 | indirect morphology | = {attribute_value}"

        # | LATERALITY | -> | Side | 182353008 (<=)
        laterality_attribute_template = "272741003 | laterality | = {attribute_value}"

        # | MEASUREMENT METHOD | -> | Laboratory procedure categorized by method | 127789004(<=)
        measurement_method_attribute_template = "370129005 | measurement method | = {attribute_value}"

        # | METHOD | -> | Action | 129264002 (<<)
        method_attribute_template = "260686004 | method | = {attribute_value}"

        # | PRIORITY | -> | Priorities | 272125009 (<=)(< Q)
        priority_attribute_template = "260870009 | priority | = {attribute_value}"


        # | PROCEDURE CONTEXT | -> | Context values for actions | 288532009 (<=)(< Q)
        procedure_context_attribute_template = "408730004 | procedure context | = {attribute_value}"

        # | PROCEDURE DEVICE | -> | Device | 49062001 (<<)
        procedure_device_attribute_template = "405815000 | procedure device | = {attribute_value}"

        # | PROCEDURE MORPHOLOGY | -> | Morphologically abnormal structure | 49755003 (<<)
        procedure_morphology_attribute_template = "405816004 | procedure morphology | = {attribute_value}"


        # | PROCEDURE SITE | -> | Anatomical or acquired body structure | 442083009 (<<)
        procedure_site_attribute_template = "363704007 | procedure site | = {attribute_value}"

        # | Procedure site - Direct | -> | Anatomical or acquired body structure | 442083009 (<<)
        direct_procedure_site_attribute_template = "405813007 | procedure site - direct | = {attribute_value}"

        # | Procedure site - Indirect | -> | Anatomical or acquired body structure | 442083009 (<<)
        indirect_procedure_site_attribute_template = "405813007 | procedure site - direct | = {attribute_value}"

        # | PROPERTY | -> | Property of measurement | 118598001 (<=)(< Q)
        property_attribute_template = "370130000 | property | = {attribute_value}"

        # | RECIPIENT CATEGORY | -> | Person | 125676002 (<<)
        #                        -> | Family | 35359004 (<<)
        #                        -> | Community | 133928008 (<<)
        #                        -> | Donor for medical or surgical procedure | 105455006 (<<)
        #                        -> | Group | 389109008 (<<)
        recipient_category_attribute_template = "370131001 | recipient category | = {attribute_value}"

        # | REVISION STATUS | -> | Primary operation | 261424001 (<<)
        #                     -> | Revision - value | 255231005 (<<)
        #                     -> | Part of multistage procedure | 257958009 (<<)
        revision_status_attribute_template = "246513007 | revision status | = {attribute_value}"



        # | ROUTE OF ADMINISTRATION | -> | Route of administration value | 284009009 (<<)
        route_of_administration_attribute_template = "410675002 | route of administration| = {attribute_value}"

        # | SCALE TYPE | -> | Quantitative | 30766002 (<<)
        #                -> | Qualitative | 26716007 (<<)
        #                -> | Ordinal value | 117363000 (<<)
        #                -> | Ordinal or quantitative value | 117365007 (<<)
        #                -> | Nominal value | 117362005 (<<)
        #                -> | Narrative value | 117364006 (<<)
        #                -> | Text value | 117444000 (<<)
        scale_type_attribute_template = "370132008 | scale type | = {attribute_value}"


        # | SPECIMEN PROCEDURE | -> | Procedure | 71388002 (<)
        specimen_procedure_attribute_template = "118171006 | specimen procedure | = {attribute_value}"

        # | SPECIMEN SOURCE IDENTITY | -> | Person | 125676002 (<<)
        #                              -> | Family | 35359004 (<<)
        #                              -> | Community | 133928008 (<<)
        #                              -> | Device | 49062001 (<<)
        #                              -> | Environment | 276339004 (<<)
        specimen_source_identity_attribute_template = "118170007 | specimen source identity | = {attribute_value}"

        # | SPECIMEN SOURCE MORPHOLOGY | -> | Morphologically abnormal structure | 49755003 (<<)
        specimen_source_morphology_attribute_template = "118168003 | specimen source morphology | = {attribute_value}"

        # | SPECIMEN SOURCE TOPOGRAPHY | -> | Anatomical or acquired body structure | 442083009 (<<)
        specimen_source_topography_attribute_template = "118169006 | specimen source topography | = {attribute_value}"

        # | SPECIMEN SUBSTANCE | -> | Substance | 105590001 (<<)
        specimen_substance_attribute_template = "370133003 | specimen substance | = {attribute_value}"

        # | SUBJECT RELATIONSHIP CONTEXT | -> | Person | 125676002 (<=)(< Q)
        subject_relationship_context_attribute_template = "408732007 | subject relationship context | = {attribute_value}"

        # | SURGICAL APPROACH | -> | Procedural approach | 103379005 (<=)(< Q)
        surgical_approach_attribute_template = "424876005 | surgical approach | = {attribute_value}"

        # | TEMPORAL CONTEXT | -> | Temporal context value | 410510008 (<=)(< Q)
        temporal_context_attribute_template = "408731000 | temporal context | = {attribute_value}"

        # | TIME ASPECT | -> | Time frame | 7389001 (<=)(< Q)
        time_aspect_attribute_template = "370134009 | time aspect | = {attribute_value}"

        # | USING ACCESS DEVICE | -> | Device | 49062001 (<<)
        using_access_device_attribute_template = "425391005 | using access device | = {attribute_value}"

        # | USING DEVICE | -> | Device | 49062001 (<<)
        using_device_attribute_template = "424226004 | using device | = {attribute_value}"

        # | USING ENERGY | -> | Physical force | 78621006 (<<)
        using_energy_attribute_template = "424244007 | using energy | = {attribute_value}"

        # | USING SUBSTANCE | -> | Substance | 105590001 (<<)
        using_substance_attribute_template = "424361007 | using substance | = {attribute_value}"
