expressions = ["""404684003 | clinical finding |""",

               """<< 404684003 | clinical finding |""",

               """> 40541001 | acute pulmonary edema |""",

               """>> 40541001 | acute pulmonary edema |""",

               """^ 700043003 | example problem list concepts reference set |""",

               """*""",

               """< 19829001 | disorder of lung | :
               116676008 | associated morphology | = 79654002 | edema |""",

               """< 19829001 | disorder of lung | :
               116676008 | associated morphology | = << 79654002 | edema |""",

               """< 404684003 | clinical finding | :
               363698007 | finding site | = << 39057004 | pulmonary valve structure | ,
               116676008 | associated morphology | = << 415582006 | stenosis |""",

               """* : 246075003 | causative agent | = 387517004 | paracetamol |""",

               """< 404684003 | clinical finding | :
               { 363698007 | finding site | = << 39057004 | pulmonary valve structure | ,
               116676008 | associated morphology | = << 415582006 | stenosis | } ,
               { 363698007 | finding site | = << 53085002 | right ventricular structure | ,
               116676008 | associated morphology | = << 56246009 | hypertrophy | }""",

               """< 404684003 |clinical finding|:
               47429007 |associated with| = (< 404684003 |clinical finding|:
               116676008 |associated morphology| = << 55641003 |infarct|)""",

               """< 27658006 |amoxicillin |:
               411116001 |has dose form| = << 385049006 |capsule|,
               { 111115 |has basis of strength| = ( 111115 |amoxicillin only|:
               111115 |strength magnitude| >= #500 ,
               111115 |strength unit| = 258684004 |mg|)}""",

               """< 27658006 |amoxicillin |:
               411116001 |has dose form| = << 385049006 |capsule|,
               { 111115 |has basis of strength| = ( 111115 |amoxicillin only|:
               111115 |strength magnitude| >= #500 ,   111115 |strength magnitude| <= #800 ,
               111115 |strength unit| = 258684004 |mg|)}""",

               """< 373873005 |pharmaceutical / biologic product|:
               111115 |trade name| = "PANADOL" """,

               """< 105590001 |substance|:
               R 127489000 |has active ingredient| = 111115 |TRIPHASIL tablet|""",

               """< 404684003 |clinical finding|: * = 79654002 |edema|""",

               """< 404684003 |clinical finding|: 116676008 |associated morphology| = *""",

               """< 373873005 |pharmaceutical / biologic product|:
               [1..3] 127489000 |has active ingredient| = < 105590001 |substance|""",

               """< 373873005 |pharmaceutical / biologic product|:
               [1..1] 127489000 |has active ingredient| = < 105590001 |substance|""",

               """< 373873005 |pharmaceutical / biologic product|:
               [0..1] 127489000 |has active ingredient| = < 105590001 |substance|""",

               """< 373873005 |pharmaceutical / biologic product|:
               [1..*] 127489000 |has active ingredient| = < 105590001 |substance|""",

               """< 404684003 |clinical finding|:
               [1..1] 363698007 |finding site| = < 91723000 |anatomical structure|""",

               """< 404684003 |clinical finding|:
               [2..*] 363698007 |finding site| = < 91723000 |anatomical structure|""",

               """< 404684003 |clinical finding|:
               { [2..*] 363698007 |finding site| = < 91723000 |anatomical structure| }""",

               """< 373873005 |pharmaceutical / biologic product|:
               [1..3] { [1..*] 127489000 |has active ingredient| = < 105590001 |substance|}""",

               """< 373873005 |pharmaceutical / biologic product|:
               [0..1] { 127489000 |has active ingredient| = < 105590001 |substance|}""",

               """< 373873005 |pharmaceutical / biologic product|:
               [1..*] { 127489000 |has active ingredient| = < 105590001 |substance|}""",

               """< 373873005 |pharmaceutical / biologic product|:
               [1..*] { [1..*] 127489000 |has active ingredient| = < 105590001 |substance|}""",

               """< 404684003 |clinical finding|:
               [1..1] { 363698007 |finding site| = < 91723000 |anatomical structure|}""",

               """< 404684003 |clinical finding|:
               [0..0] { [2..*] 363698007 |finding site| = < 91723000 |anatomical structure|}""",

               """< 404684003 |clinical finding|:
               363698007 |finding site| = << 39057004 |pulmonary valve structure| AND
               116676008 |associated morphology| = << 415582006 |stenosis|""",

               """< 404684003 |clinical finding|:
               116676008 |associated morphology| = << 55641003 |infarct| OR
               42752001 |due to| = << 22298006 |myocardial infarction|""",

               """< 404684003 |clinical finding|:
               ( 363698007 |finding site| = << 39057004 |pulmonary valve structure| AND
               116676008 |associated morphology| = << 415582006 |stenosis| ) AND
               42752001 |due to| = << 445238008|malignant carcinoid tumor|""",

               """< 404684003 |clinical finding| :
               ( 363698007 |finding site| = << 39057004 |pulmonary valve structure| AND
               116676008 |associated morphology| = << 415582006 |stenosis|) OR
               42752001 |due to| = << 445238008|malignant carcinoid tumor|""",

               """< 19829001 |disorder of lung| AND < 301867009 |edema of trunk|""",

               """< 19829001 |disorder of lung| OR < 301867009 |edema of trunk|""",
               """< 19829001|disorder of lung| AND
               ^ 700043003 |example problem list concepts reference set|""",

               """(< 19829001 |disorder of lung| AND < 301867009 |edema of trunk|) AND
               ^ 700043003 |example problem list concepts reference set|""",

               """(< 19829001 |disorder of lung| AND < 301867009 |edema of trunk|) OR
               ^ 700043003 |example problem list concepts reference set|""",

               """< 404684003 |clinical finding|:
               { 363698007 |finding site| = << 39057004 |pulmonary valve structure|,
               116676008 |associated morphology| = << 415582006 |stenosis|} OR
               { 363698007 |finding site| = << 53085002 |right ventricular structure|,
               116676008 |associated morphology| = << 56246009 |hypertrophy|}""",

               """^ 450990004 |adverse drug reactions reference set for GP/FP health issue|:
               246075003 |causative agent| =
               (< 373873005 |pharmaceutical / biologic product| OR < 105590001 |substance|)""",

               """< 404684003 |clinical finding|: 116676008 |associated morphology| =
               (<< 56208002|ulcer| AND << 50960005|hemorrhage|)""",

               """<< 19829001 |disorder of lung| MINUS << 301867009 |edema of trunk|""",

               """<< 19829001 |disorder of lung| MINUS ^ 700043003 |example problem list concepts reference set|""",

               """< 404684003 |clinical finding|: 116676008 |associated morphology| =
               ((<< 56208002 |ulcer| AND << 50960005 |hemorrhage|) MINUS << 26036001 |obstruction|)""",

               """< 404684003 |clinical finding|:
               116676008 |associated morphology| !=  << 26036001 |obstruction|""",

               """< 404684003 |clinical finding|:
               [0..0] 116676008 |associated morphology| =  << 26036001 |obstruction|""",

               """< 404684003 |clinical finding|:
               [0..0] 116676008 |associated morphology| != << 26036001 |obstruction|""",

               """< 404684003 |clinical finding|:
               [0..0] 116676008 |associated morphology| !=  << 26036001 |obstruction| and
               [1..*] 116676008 |associated morphology| =   << 26036001 |obstruction|""",

               """< ^ 700043003 |example problem list concepts reference set|""",

               """(< 19829001|disorder of lung| OR ^ 700043003 |example problem list concepts reference set|)
               MINUS ^ 450976002|disorders and diseases reference set for GP/FP reason for encounter|""",

               """(< 19829001|disorder of lung| MINUS ^ 700043003 |example problem list concepts reference set|) MINUS
               ^ 450976002|disorders and diseases reference set for GP/FP reason for encounter|""",

               """< 19829001|disorder of lung| OR ^ 700043003 |example problem list concepts reference set| OR
               ^ 450976002|disorders and diseases reference set for GP/FP reason for encounter|"""
]
