from unittest import TestCase
from snomedct_terminology_server.server.models import Concept
from snomedct_terminology_server.server.expressions.parse_expression_language import (
    constraint_language_sctids,)
from snomedct_terminology_server.server.expressions.helpers import ExpressionSyntaxError


class TestECL(TestCase):
    def test_ecl_concept_model(self):
        assert constraint_language_sctids('404684003 | clinical finding |') == ['404684003']

        with self.assertRaises(ExpressionSyntaxError):
            constraint_language_sctids('404 | clinical finding |')

        assert len(Concept.objects.filter(id__in=[404684003], active=True)) == len([404684003])

        assert constraint_language_sctids('<< 404684003 | clinical finding |') == ['404684003']

        assert len(Concept.objects.filter(id__in=[404684003], active=True)) == len([404684003])

        assert constraint_language_sctids('> 40541001 | acute pulmonary edema |') == ['40541001']

        assert len(Concept.objects.filter(id__in=[40541001], active=True)) == len([40541001])

        assert constraint_language_sctids('>> 40541001 | acute pulmonary edema |') == ['40541001']

        assert len(Concept.objects.filter(id__in=[40541001], active=True)) == len([40541001])

        assert constraint_language_sctids(
            """
^ 8454811000001105 | example problem list concepts reference set |""") == ['8454811000001105']

        assert len(Concept.objects.filter(id__in=[8454811000001105],
                                          active=True)) == len([8454811000001105])

        assert constraint_language_sctids(
            """< 19829001 | disorder of lung | :
116676008 | associated morphology | = 79654002 | edema |""") == ['19829001',
                                                                 '116676008', '79654002']

        assert len(Concept.objects.filter(
            id__in=[19829001, 116676008, 79654002],
            active=True)) == len([19829001, 116676008, 79654002])

        assert constraint_language_sctids(
            """< 19829001 | disorder of lung | :
116676008 | associated morphology | = << 79654002 | edema |""") == ['19829001',
                                                                    '116676008',
                                                                    '79654002']

        assert len(Concept.objects.filter(
            id__in=[19829001, 116676008, 79654002],
            active=True)) == len([19829001, 116676008, 79654002])

        assert constraint_language_sctids("""< 404684003 | clinical finding | :
363698007 | finding site | = << 39057004 | pulmonary valve structure | ,
116676008 | associated morphology | = << 415582006 | stenosis |""") == ['404684003', '363698007',
                                                                        '39057004', '116676008',
                                                                        '415582006']

        assert len(Concept.objects.filter(
            id__in=[404684003, 363698007, 39057004, 116676008, 415582006],
            active=True)) == len([404684003, 363698007, 39057004, 116676008, 415582006])

        assert constraint_language_sctids("""* : 246075003 | causative agent | =
387517004 | paracetamol |""") == ['246075003', '387517004']

        assert len(Concept.objects.filter(
            id__in=[246075003, 387517004],
            active=True)) == len([246075003, 387517004])

        assert constraint_language_sctids("""< 404684003 | clinical finding | :
{ 363698007 | finding site | = << 39057004 | pulmonary valve structure | ,
116676008 | associated morphology | = << 415582006 | stenosis | } ,
{ 363698007 | finding site | = << 53085002 | right ventricular structure | ,
116676008 | associated morphology | = << 56246009 | hypertrophy | }""") == ['404684003',
                                                                            '363698007',
                                                                            '39057004',
                                                                            '116676008',
                                                                            '415582006',
                                                                            '363698007',
                                                                            '53085002',
                                                                            '116676008',
                                                                            '56246009']

        assert len(Concept.objects.filter(
            id__in=set([404684003, 363698007, 39057004, 116676008, 415582006,
                        363698007, 53085002, 116676008, 56246009]),
            active=True)) == len(set([404684003, 363698007, 39057004, 116676008,
                                      415582006, 363698007, 53085002, 116676008, 56246009]))

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
47429007 |associated with| = (< 404684003 |clinical finding|:
116676008 |associated morphology| = << 55641003 |infarct|)""") == ['404684003', '47429007',
                                                                   '404684003', '116676008',
                                                                   '55641003']

        assert len(Concept.objects.filter(
            id__in=set([404684003, 47429007, 404684003,
                        116676008, 55641003]), active=True)) == len(set([404684003, 47429007,
                                                                         404684003, 116676008,
                                                                         55641003]))

        assert constraint_language_sctids("""< 27658006 |amoxicillin |:
411116001 |has dose form| = << 385049006 |capsule|,
{ 108003 |has basis of strength| = ( 108003 |amoxicillin only|:
108003 |strength magnitude| >= #500 ,
108003 |strength unit| = 258684004 |mg|)}""") == ['27658006', '411116001', '385049006', '108003',
                                                  '108003', '108003', '108003', '258684004']

        assert len(Concept.objects.filter(
            id__in=set([27658006, 411116001, 385049006, 108003,
                        108003, 108003, 108003, 258684004]),
            active=True)) == len(set([27658006, 411116001, 385049006, 108003,
                                      108003, 108003, 108003, 258684004]))

        assert constraint_language_sctids("""< 27658006 |amoxicillin |:
411116001 |has dose form| = << 385049006 |capsule|,
{ 108003 |has basis of strength| = ( 108003 |amoxicillin only|:
108003 |strength magnitude| >= #500 ,   108003 |strength magnitude| <= #800 ,
108003 |strength unit| = 258684004 |mg|)}""") == ['27658006', '411116001', '385049006', '108003',
                                                  '108003', '108003', '108003', '108003',
                                                  '258684004']

        assert len(Concept.objects.filter(
            id__in=set([27658006, 411116001, 385049006, 108003,
                        108003, 108003, 108003, 108003, 258684004]),
            active=True)) == len(set([27658006, 411116001, 385049006, 108003,
                                      108003, 108003, 108003, 108003, 258684004]))

        assert constraint_language_sctids("""< 373873005 |pharmaceutical / biologic product|:
108003 |trade name| = "PANADOL" """) == ['373873005', '108003']

        assert len(Concept.objects.filter(
            id__in=[373873005, 108003],
            active=True)) == len([373873005, 108003])

        assert constraint_language_sctids("""< 105590001 |substance|:
R 127489000 |has active ingredient| = 108003 |TRIPHASIL tablet|""") == ['105590001',
                                                                        '127489000', '108003']

        assert len(Concept.objects.filter(
            id__in=[105590001, 127489000, 108003],
            active=True)) == len([105590001, 127489000, 108003])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
* = 79654002 |edema|""") == ['404684003', '79654002']

        assert len(Concept.objects.filter(
            id__in=[404684003, 79654002], active=True)) == len([404684003, 79654002])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
116676008 |associated morphology| = *""") == ['404684003', '116676008']

        assert len(Concept.objects.filter(
            id__in=[404684003, 116676008],
            active=True)) == len([404684003, 116676008])

        assert constraint_language_sctids("""< 373873005 |pharmaceutical / biologic product|:
[1..3] 127489000 |has active ingredient| =
< 105590001 |substance|""") == ['373873005', '127489000', '105590001']

        assert len(Concept.objects.filter(id__in=[373873005, 127489000, 105590001],
                                          active=True)) == len([373873005, 127489000, 105590001])

        assert constraint_language_sctids("""< 373873005 |pharmaceutical / biologic product|:
[1..1] 127489000 |has active ingredient| = < 105590001 |substance|""") == ['373873005', '127489000',
                                                                           '105590001']

        assert len(Concept.objects.filter(id__in=[373873005, 127489000, 105590001],
                                          active=True)) == len([373873005, 127489000, 105590001])

        assert constraint_language_sctids("""< 373873005 |pharmaceutical / biologic product|:
[0..1] 127489000 |has active ingredient| =
< 105590001 |substance|""") == ['373873005', '127489000', '105590001']

        assert len(Concept.objects.filter(
            id__in=[373873005, 127489000, 105590001],
            active=True)) == len([373873005, 127489000, 105590001])

        assert constraint_language_sctids("""< 373873005 |pharmaceutical / biologic product|:
[1..*] 127489000 |has active ingredient| =
< 105590001 |substance|""") == ['373873005', '127489000', '105590001']

        assert len(Concept.objects.filter(
            id__in=[373873005, 127489000, 105590001],
            active=True)) == len([373873005, 127489000, 105590001])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
[1..1] 363698007 |finding site| = < 91723000 |anatomical structure|""") == ['404684003',
                                                                            '363698007', '91723000']

        assert len(Concept.objects.filter(
            id__in=[404684003, 363698007, 91723000],
            active=True)) == len([404684003, 363698007, 91723000])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
[2..*] 363698007 |finding site| = < 91723000 |anatomical structure|""") == ['404684003',
                                                                            '363698007', '91723000']

        assert len(Concept.objects.filter(
            id__in=[404684003, 363698007, 91723000],
            active=True)) == len([404684003, 363698007, 91723000])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
{ [2..*] 363698007 |finding site| =
< 91723000 |anatomical structure| }""") == ['404684003', '363698007', '91723000']

        assert len(Concept.objects.filter(
            id__in=[404684003, 363698007, 91723000],
            active=True)) == len([404684003, 363698007, 91723000])

        assert constraint_language_sctids("""< 373873005 |pharmaceutical / biologic product|:
[1..3] { [1..*] 127489000 |has active ingredient| =
< 105590001 |substance|}""") == ['373873005', '127489000', '105590001']

        assert len(Concept.objects.filter(
            id__in=[373873005, 127489000, 105590001],
            active=True)) == len([373873005, 127489000, 105590001])

        assert constraint_language_sctids("""< 373873005 |pharmaceutical / biologic product|:
[0..1] { 127489000 |has active ingredient| =
< 105590001 |substance|}""") == ['373873005', '127489000', '105590001']

        assert len(Concept.objects.filter(
            id__in=[373873005, 127489000, 105590001],
            active=True)) == len([373873005, 127489000, 105590001])

        assert constraint_language_sctids("""< 373873005 |pharmaceutical / biologic product|:
[1..*] { 127489000 |has active ingredient| =
< 105590001 |substance|}""") == ['373873005', '127489000', '105590001']

        assert len(Concept.objects.filter(
            id__in=[373873005, 127489000, 105590001],
            active=True)) == len([373873005, 127489000, 105590001])

        assert constraint_language_sctids("""< 373873005 |pharmaceutical / biologic product|:
[1..*] { [1..*] 127489000 |has active ingredient| =
< 105590001 |substance|}""") == ['373873005', '127489000', '105590001']

        assert len(Concept.objects.filter(
            id__in=[373873005, 127489000, 105590001],
            active=True)) == len([373873005, 127489000, 105590001])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
[1..1] { 363698007 |finding site| =
< 91723000 |anatomical structure|}""") == ['404684003', '363698007', '91723000']

        assert len(Concept.objects.filter(
            id__in=[404684003, 363698007, 91723000],
            active=True)) == len([404684003, 363698007, 91723000])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
[0..0] { [2..*] 363698007 |finding site| =
< 91723000 |anatomical structure|}""") == ['404684003', '363698007', '91723000']

        assert len(Concept.objects.filter(
            id__in=[404684003, 363698007, 91723000],
            active=True)) == len([404684003, 363698007, 91723000])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
363698007 |finding site| = << 39057004 |pulmonary valve structure| AND
116676008 |associated morphology| =
<< 415582006 |stenosis|""") == ['404684003', '363698007', '39057004', '116676008', '415582006']

        assert len(Concept.objects.filter(
            id__in=[404684003, 363698007, 39057004, 116676008, 415582006],
            active=True)) == len([404684003, 363698007, 39057004, 116676008, 415582006])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
116676008 |associated morphology| = << 55641003 |infarct| OR
42752001 |due to| = << 22298006 |myocardial infarction|""") == ['404684003', '116676008',
                                                                '55641003', '42752001',
                                                                '22298006']

        assert len(Concept.objects.filter(
            id__in=[404684003, 116676008, 55641003, 42752001, 22298006],
            active=True)) == len([404684003, 116676008, 55641003, 42752001, 22298006])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
( 363698007 |finding site| = << 39057004 |pulmonary valve structure| AND
116676008 |associated morphology| = << 415582006 |stenosis| ) AND
42752001 |due to| = << 445238008|malignant carcinoid tumor|""") == ['404684003', '363698007',
                                                                    '39057004', '116676008',
                                                                    '415582006', '42752001',
                                                                    '445238008']

        assert len(Concept.objects.filter(
            id__in=[404684003, 363698007, 39057004,
                    116676008, 415582006, 42752001, 445238008],
            active=True)) == len([404684003, 363698007, 39057004,
                                  116676008, 415582006, 42752001, 445238008])

        assert constraint_language_sctids("""< 404684003 |clinical finding| :
( 363698007 |finding site| = << 39057004 |pulmonary valve structure| AND
116676008 |associated morphology| = << 415582006 |stenosis|) OR
42752001 |due to| = << 445238008|malignant carcinoid tumor|""") == ['404684003', '363698007',
                                                                    '39057004', '116676008',
                                                                    '415582006', '42752001',
                                                                    '445238008']

        assert len(Concept.objects.filter(
            id__in=[404684003, 363698007, 39057004,
                    116676008, 415582006, 42752001, 445238008],
            active=True)) == len([404684003, 363698007, 39057004,
                                  116676008, 415582006, 42752001, 445238008])

        assert constraint_language_sctids(
            """< 19829001 |disorder of lung| AND < 301867009 |edema of trunk|""") == ['19829001',
                                                                                      '301867009']

        assert len(Concept.objects.filter(id__in=[19829001, 301867009],
                                          active=True)) == len([19829001, 301867009])

        assert constraint_language_sctids(
            """< 19829001 |disorder of lung| OR < 301867009 |edema of trunk|""") == ['19829001',
                                                                                     '301867009']

        assert len(Concept.objects.filter(
            id__in=[19829001, 301867009],
            active=True)) == len([19829001, 301867009])

        assert constraint_language_sctids("""< 19829001|disorder of lung| AND
^ 8454811000001105 |example problem list concepts reference set|""") == ['19829001',
                                                                         '8454811000001105']

        assert len(Concept.objects.filter(
            id__in=[19829001, 8454811000001105],
            active=True)) == len([19829001, 8454811000001105])

        assert constraint_language_sctids("""
(< 19829001 |disorder of lung| AND < 301867009 |edema of trunk|) AND
^ 8454811000001105 |example problem list concepts reference set|""") == ['19829001', '301867009',
                                                                         '8454811000001105']

        assert len(Concept.objects.filter(
            id__in=[19829001, 301867009, 8454811000001105],
            active=True)) == len([19829001, 301867009, 8454811000001105])

        assert constraint_language_sctids(
            """(< 19829001 |disorder of lung| AND < 301867009 |edema of trunk|) OR
^ 8454811000001105 |example problem list concepts reference set|""") == ['19829001',
                                                                         '301867009',
                                                                         '8454811000001105']

        assert len(Concept.objects.filter(
            id__in=[19829001, 301867009, 8454811000001105],
            active=True)) == len([19829001, 301867009, 8454811000001105])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
{ 363698007 |finding site| = << 39057004 |pulmonary valve structure|,
116676008 |associated morphology| = << 415582006 |stenosis|} OR
{ 363698007 |finding site| = << 53085002 |right ventricular structure|,
116676008 |associated morphology| = << 56246009 |hypertrophy|}""") == ['404684003', '363698007',
                                                                       '39057004', '116676008',
                                                                       '415582006', '363698007',
                                                                       '53085002', '116676008',
                                                                       '56246009']

        assert len(Concept.objects.filter(
            id__in=set([404684003, 363698007, 39057004, 116676008,
                        415582006, 363698007, 53085002, 116676008, 56246009]),
            active=True)) == len(set([404684003, 363698007, 39057004, 116676008,
                                      415582006, 363698007, 53085002, 116676008, 56246009]))

        assert constraint_language_sctids(
            """^ 450990004 |adverse drug reactions reference set for GP/FP health issue|:
246075003 |causative agent| =
(< 373873005 |pharmaceutical / biologic product| OR < 105590001 |substance|)""") == ['450990004',
                                                                                     '246075003',
                                                                                     '373873005',
                                                                                     '105590001']

        assert len(Concept.objects.filter(
            id__in=[450990004, 246075003, 373873005, 105590001],
            active=True)) == len([450990004, 246075003, 373873005, 105590001])

        assert constraint_language_sctids(
            """< 404684003 |clinical finding|: 116676008 |associated morphology| =
(<< 56208002|ulcer| AND << 50960005|hemorrhage|)""") == ['404684003', '116676008',
                                                         '56208002', '50960005']

        assert len(Concept.objects.filter(
            id__in=[404684003, 116676008, 56208002, 50960005],
            active=True)) == len([404684003, 116676008, 56208002, 50960005])

        assert constraint_language_sctids(
            """<< 19829001 |disorder of lung| MINUS
<< 301867009 |edema of trunk|""") == ['19829001', '301867009']

        assert len(Concept.objects.filter(
            id__in=[19829001, 301867009],
            active=True)) == len([19829001, 301867009])

        assert constraint_language_sctids("""<< 19829001 |disorder of lung| MINUS
^ 8454811000001105 |example problem list concepts reference set|""") == ['19829001',
                                                                         '8454811000001105']

        assert len(Concept.objects.filter(
            id__in=[19829001, 8454811000001105],
            active=True)) == len([19829001, 8454811000001105])

        assert constraint_language_sctids(
            """< 404684003 |clinical finding|: 116676008 |associated morphology| =
((<< 56208002 |ulcer| AND << 50960005 |hemorrhage|) MINUS
<< 26036001 |obstruction|)""") == ['404684003', '116676008', '56208002', '50960005', '26036001']

        assert len(Concept.objects.filter(
            id__in=[404684003, 116676008, 56208002, 50960005, 26036001],
            active=True)) == len([404684003, 116676008, 56208002, 50960005, 26036001])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
116676008 |associated morphology| !=
<< 26036001 |obstruction|""") == ['404684003', '116676008', '26036001']

        assert len(Concept.objects.filter(
            id__in=[404684003, 116676008, 26036001],
            active=True)) == len([404684003, 116676008, 26036001])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
[0..0] 116676008 |associated morphology| =
<< 26036001 |obstruction|""") == ['404684003', '116676008', '26036001']

        assert len(Concept.objects.filter(
            id__in=[404684003, 116676008, 26036001],
            active=True)) == len([404684003, 116676008, 26036001])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
[0..0] 116676008 |associated morphology| !=
<< 26036001 |obstruction|""") == ['404684003', '116676008', '26036001']

        assert len(Concept.objects.filter(
            id__in=[404684003, 116676008, 26036001],
            active=True)) == len([404684003, 116676008, 26036001])

        assert constraint_language_sctids("""< 404684003 |clinical finding|:
[0..0] 116676008 |associated morphology| != << 26036001 |obstruction| and
[1..*] 116676008 |associated morphology| =
<< 26036001 |obstruction|""") == ['404684003', '116676008', '26036001', '116676008', '26036001']

        assert len(Concept.objects.filter(
            id__in=set([404684003, 116676008, 26036001, 116676008, 26036001]),
            active=True)) == len(set([404684003, 116676008, 26036001, 116676008, 26036001]))

        assert constraint_language_sctids(
            """
< ^ 8454811000001105 |example problem list concepts reference set|""") == ['8454811000001105']

        assert len(Concept.objects.filter(
            id__in=[8454811000001105], active=True)) == len([8454811000001105])

        assert constraint_language_sctids(
            """(< 19829001|disorder of lung|
OR
^ 8454811000001105 |example problem list concepts reference set|)
MINUS
^ 450976002|disorders and diseases reference set for GP/FP reason for encounter|
            """) == ['19829001',
                     '8454811000001105', '450976002']

        assert len(Concept.objects.filter(
            id__in=[19829001, 8454811000001105, 450976002],
            active=True)) == len([19829001, 8454811000001105, 450976002])

        assert constraint_language_sctids(
            """(< 19829001|disorder of lung| MINUS
^ 8454811000001105 |example problem list concepts reference set|) MINUS
^ 450976002|disorders and diseases reference set for GP/FP reason for encounter|
""") == ['19829001', '8454811000001105', '450976002']

        assert len(Concept.objects.filter(
            id__in=[19829001, 8454811000001105, 450976002],
            active=True)) == len([19829001, 8454811000001105, 450976002])

        assert constraint_language_sctids("""< 19829001|disorder of lung| OR
^ 8454811000001105 |example problem list concepts reference set| OR
^ 450976002|disorders and diseases reference set for GP/FP reason for encounter|
""") == ['19829001',
         '8454811000001105', '450976002']
        assert len(Concept.objects.filter(
            id__in=[19829001, 8454811000001105, 450976002],
            active=True)) == len([19829001, 8454811000001105, 450976002])
