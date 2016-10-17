from unittest import TestCase
from snomedct_terminology_server.server.models import Concept
from snomedct_terminology_server.server.expressions.parse_compositional_grammar import (
    compositional_grammar_sctids,)


class TestCompositionalGrammarConceptModel(TestCase):
    def test_compositional_grammar_concept_model(self):
        assert compositional_grammar_sctids("""71388002 | procedure | :
{ 260686004 | method | = 129304002 | excision - action | ,
405813007 | procedure site - direct | = 20837000 | structure of right ovary | ,
424226004 | using device | = 122456005 | laser device | }
{260686004 | method | = 261519002 | diathermy excision - action | ,
405813007 | procedure site - direct | =
113293009 | structure of left fallopian tube | }""") == ['71388002',
                                                         '260686004',
                                                         '129304002',
                                                         '405813007',
                                                         '20837000',
                                                         '424226004',
                                                         '122456005',
                                                         '260686004',
                                                         '261519002',
                                                         '405813007',
                                                         '113293009']
        assert len(Concept.objects.filter(id__in=set([71388002, 260686004, 129304002,
                                                      20837000, 424226004, 122456005, 260686004,
                                                      261519002, 405813007, 113293009]),
                                          active=True)) == len(
                                              set([71388002, 260686004, 129304002, 20837000,
                                                   424226004, 122456005, 260686004, 261519002,
                                                   405813007, 113293009]))

        assert compositional_grammar_sctids("""373873005 |pharmaceutical / biologic product|:
411116001 |has dose form| = 385049006 |capsule|,
108003 |active ingredient count| = #1,
{127489000 |has active ingredient| = 96068000 |amoxicillin trihydrate|,
108003 |has reference basis of strength| = 372687004 |amoxicillin|,
108003 |strength magnitude equal to| = #500,
108003 |strength unit| = 258684004 |mg|}""") == ['373873005', '411116001', '385049006', '108003',
                                                 '127489000', '96068000', '108003',
                                                 '372687004', '108003', '108003', '258684004']

        assert len(Concept.objects.filter(id__in=set([373873005, 411116001, 385049006, 108003,
                                                      127489000, 96068000, 108003, 372687004,
                                                      108003, 108003, 258684004]),
                                          active=True)) == len(set([373873005, 411116001,
                                                                    385049006, 108003, 127489000,
                                                                    96068000, 108003, 372687004,
                                                                    108003, 108003, 258684004]))

        assert compositional_grammar_sctids("""71388002 |procedure|:
{ 260686004 |method| = 129304002 |excision - action|,
405813007 |procedure site - direct| = 15497006 |ovarian structure|}
{ 260686004 |method| = 129304002 |excision - action|,
405813007 |procedure site - direct| = 31435000 |fallopian tube structure|}""") == ['71388002',
                                                                                   '260686004',
                                                                                   '129304002',
                                                                                   '405813007',
                                                                                   '15497006',
                                                                                   '260686004',
                                                                                   '129304002',
                                                                                   '405813007',
                                                                                   '31435000']

        assert len(Concept.objects.filter(
            id__in=set([71388002, 260686004, 129304002, 405813007,
                        15497006, 260686004, 129304002, 405813007, 31435000]),
            active=True)) == len(set([71388002, 260686004, 129304002, 405813007,
                                      15497006, 260686004, 129304002, 405813007, 31435000]))

        assert compositional_grammar_sctids("""373873005 |pharmaceutical / biologic product|:
411116001 |has dose form| = 385023001 |oral solution|,
108003 |active ingredient count| = #1,
{127489000 |has active ingredient| = 372897005 |albuterol|,
108003 |has reference basis of strength| = 372897005 |albuterol|,
108003 |strength magnitude equal to | = #0.083,
108003 |strength unit| = 118582008 |%|}""") == ['373873005', '411116001', '385023001', '108003',
                                                '127489000', '372897005', '108003', '372897005',
                                                '108003', '108003', '118582008']

        assert len(Concept.objects.filter(
            id__in=set([373873005, 411116001, 385023001, 108003, 127489000,
                        372897005, 108003, 372897005, 108003, 108003, 118582008]),
            active=True)) == len(set([373873005, 411116001, 385023001, 108003, 127489000,
                                      372897005, 108003, 372897005, 108003, 108003, 118582008]))

        assert compositional_grammar_sctids(
            """322236009 |paracetamol 500 mg tablet|:
108003 |trade name| = "PANADOL" """) == ['322236009', '108003']

        assert len(
            Concept.objects.filter(id__in=[322236009, 108003],
                                   active=True)) == len([322236009, 108003])

        assert compositional_grammar_sctids("""373873005 |pharmaceutical / biologic product|:
411116001 |has dose form| = 385218009 |injection|,
108003 |active ingredient count| = #2,
{ 127489000 |has active ingredient| = 428126001 |diphtheria toxoid|,
108003 |has reference basis of strength | = 428126001 |diphtheria toxoid|,
108003 |strength magnitude minimum| = #4,
108003 |strength unit| = 259002007 |IU/mL|}
{ 127489000 |has active ingredient| = 412375000 |tetanus toxoid|,
108003 |has reference basis of strength| = 412375000 |tetanus toxoid|,
108003 |strength magnitude equal to| = #40,
        108003 |strength unit| = 259002007 |IU/mL|}""") == ['373873005', '411116001', '385218009',
                                                            '108003', '127489000', '428126001',
                                                            '108003', '428126001', '108003',
                                                            '108003', '259002007', '127489000',
                                                            '412375000', '108003', '412375000',
                                                            '108003', '108003', '259002007']

        assert len(Concept.objects.filter(
            id__in=set([373873005, 411116001, 385218009, 108003, 127489000, 428126001, 108003,
                        428126001, 108003, 108003, 259002007, 127489000, 412375000, 108003,
                        412375000, 108003, 108003, 259002007]), active=True)) == len(
                        set([373873005, 411116001, 385218009, 108003, 127489000, 428126001, 108003,
                             428126001, 108003, 108003, 259002007, 127489000, 412375000, 108003,
                             412375000, 108003, 108003, 259002007]))

        assert compositional_grammar_sctids(
            """===  46866001 |fracture of lower limb| + 428881005 |injury of tibia|:
            116676008 |associated morphology| = 72704001 |fracture|,
            363698007 |finding site| = 12611008 |bone structure of tibia|""") == ['46866001',
                                                                                  '428881005',
                                                                                  '116676008',
                                                                                  '72704001',
                                                                                  '363698007',
                                                                                  '12611008']

        assert len(
            Concept.objects.filter(
                id__in=[46866001, 428881005, 116676008,
                        72704001, 363698007, 12611008],
                active=True)) == len([46866001, 428881005, 116676008,
                                      72704001, 363698007, 12611008])

        assert compositional_grammar_sctids(
            """<<< 73211009 |diabetes mellitus|:
            363698007 |finding site| = 113331007 |endocrine system|""") == ['73211009', '363698007',
                                                                            '113331007']

        assert len(Concept.objects.filter(
            id__in=[73211009, 363698007, 113331007], active=True)) == len([73211009,
                                                                           363698007, 113331007])

        assert compositional_grammar_sctids("""373873005 |pharmaceutical / biologic product|:
411116001 |has dose form| =
(421720008 |spray dose form| + 7946007 |drug suspension|)""") == ['373873005', '411116001',
                                                                  '421720008', '7946007']

        assert len(Concept.objects.filter(
            id__in=[373873005, 411116001, 421720008, 7946007], active=True)) == len(
                [373873005, 411116001, 421720008, 7946007])

        assert compositional_grammar_sctids("""397956004 |prosthetic arthroplasty of the hip|:
363704007 |procedure site| = (24136001 |hip joint structure|:
272741003 |laterality| = 7771000 |left|)""") == ['397956004', '363704007', '24136001',
                                                 '272741003', '7771000']

        assert len(Concept.objects.filter(
            id__in=[397956004, 363704007, 24136001, 272741003, 7771000], active=True)) == len(
                [397956004, 363704007, 24136001, 272741003, 7771000])

        assert compositional_grammar_sctids("""397956004 |prosthetic arthroplasty of the hip|:
363704007 |procedure site| = (24136001 |hip joint structure|:
272741003 |laterality| = 7771000 |left|),
{ 363699004 |direct device| = 304120007 |total hip replacement prosthesis|,
        260686004 |method| = 257867005 |insertion - action|}""") == [
            '397956004', '363704007', '24136001',
            '272741003', '7771000', '363699004',
            '304120007', '260686004', '257867005']

        assert len(Concept.objects.filter(
            id__in=[397956004, 363704007, 24136001, 272741003, 7771000,
                    363699004, 304120007, 260686004, 257867005], active=True)) == len(
                        [397956004, 363704007, 24136001, 272741003, 7771000,
                         363699004, 304120007, 260686004, 257867005])

        assert compositional_grammar_sctids("""
243796009 |situation with explicit context|:
{ 408730004 |procedure context| = 385658003 |done|,
  408731000 |temporal context| = 410512000 |current or specified|,
  408732007 |subject relationship context| = 410604004 |subject of record|,
  363589002 |associated procedure| =
( 397956004 |prosthetic arthroplasty of the hip|:
363704007 |procedure site| = (24136001 |hip joint structure|:
272741003 |laterality| = 7771000 |left|)
{ 363699004 |direct device| = 304120007 |total hip replacement prosthesis|,
        260686004 |method| = 257867005 |insertion - action|}) }""") == ['243796009', '408730004',
                                                                        '385658003', '408731000',
                                                                        '410512000', '408732007',
                                                                        '410604004', '363589002',
                                                                        '397956004', '363704007',
                                                                        '24136001', '272741003',
                                                                        '7771000', '363699004',
                                                                        '304120007', '260686004',
                                                                        '257867005']

        assert len(Concept.objects.filter(
            id__in=[243796009, 408730004, 385658003, 408731000, 410512000, 408732007, 410604004,
                    363589002, 397956004, 363704007, 24136001, 272741003, 7771000, 363699004,
                    304120007, 260686004, 257867005], active=True)) == len([243796009, 408730004,
                                                                            385658003, 408731000,
                                                                            410512000, 408732007,
                                                                            410604004, 363589002,
                                                                            397956004, 363704007,
                                                                            24136001, 272741003,
                                                                            7771000, 363699004,
                                                                            304120007, 260686004,
                                                                            257867005])

        assert compositional_grammar_sctids("""83152002 |oophorectomy|:
405815000|procedure device| = 122456005 |laser device|""") == ['83152002', '405815000', '122456005']

        assert len(Concept.objects.filter(
            id__in=[83152002, 405815000, 122456005],
            active=True)) == len([83152002, 405815000, 122456005])

        assert compositional_grammar_sctids("""182201002 |hip joint|:
272741003 |laterality| = 24028007 |right|""") == ['182201002', '272741003', '24028007']

        assert len(Concept.objects.filter(
            id__in=[182201002, 272741003, 24028007],
            active=True)) == len([182201002, 272741003, 24028007])

        assert compositional_grammar_sctids("""71388002 |procedure|:
405815000|procedure device| = 122456005 |laser device|,
260686004 |method| = 129304002 |excision - action|,
405813007 |procedure site - direct| = 15497006 |ovarian structure|""") == ['71388002',
                                                                           '405815000',
                                                                           '122456005',
                                                                           '260686004',
                                                                           '129304002',
                                                                           '405813007',
                                                                           '15497006']

        assert len(Concept.objects.filter(
            id__in=[71388002, 405815000, 122456005, 260686004, 129304002, 405813007, 15497006],
            active=True)) == len([71388002, 405815000, 122456005,
                                  260686004, 129304002, 405813007, 15497006])

        assert compositional_grammar_sctids("""65801008 |excision|:
405813007 |procedure site - direct| = 66754008 |appendix structure|,
260870009 |priority| = 25876001 |emergency|""") == ['65801008', '405813007',
                                                    '66754008', '260870009', '25876001']

        assert len(Concept.objects.filter(
            id__in=[65801008, 405813007, 66754008, 260870009, 25876001],
            active=True)) == len([65801008, 405813007, 66754008,
                                  260870009, 25876001])

        assert compositional_grammar_sctids(
            """313056006 |epiphysis of ulna|:
272741003 |laterality| = 7771000 |left|""") == ['313056006', '272741003', '7771000']

        assert len(Concept.objects.filter(
            id__in=[313056006, 272741003, 7771000],
            active=True)) == len([313056006, 272741003, 7771000])

        assert compositional_grammar_sctids(
            """119189000 |ulna part| + 312845000 |epiphysis of upper limb|:
272741003 |laterality| = 7771000 |left|""") == ['119189000', '312845000',
                                                '272741003', '7771000']

        assert len(Concept.objects.filter(
            id__in=[119189000, 312845000, 272741003, 7771000],
            active=True)) == len([119189000, 312845000, 272741003, 7771000])

        assert compositional_grammar_sctids(
            """421720008 |spray dose form| + 7946007 |drug suspension|"""
        ) == ['421720008', '7946007']

        assert len(Concept.objects.filter(
            id__in=[421720008, 7946007],
            active=True)) == len([421720008, 7946007])

        assert compositional_grammar_sctids(
            """421720008 + 7946007 |drug suspension|""") == ['421720008',
                                                             '7946007']

        assert len(Concept.objects.filter(
            id__in=[421720008, 7946007],
            active=True)) == len([421720008, 7946007])

        assert compositional_grammar_sctids("""421720008
+ 7946007
|drug suspension|""") == ['421720008', '7946007']

        assert len(Concept.objects.filter(
            id__in=[421720008, 7946007],
            active=True)) == len([421720008, 7946007])

        assert compositional_grammar_sctids('73211009 |diabetes mellitus|') == ['73211009']

        assert len(Concept.objects.filter(
            id__in=[73211009],
            active=True)) == len([73211009])

        assert compositional_grammar_sctids('73211009') == ['73211009']

        assert len(Concept.objects.filter(
            id__in=[73211009],
            active=True)) == len([73211009])
