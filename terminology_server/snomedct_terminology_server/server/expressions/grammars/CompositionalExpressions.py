expressions = [
    """71388002 | procedure | :
{ 260686004 | method | = 129304002 | excision - action | ,
405813007 | procedure site - direct | = 20837000 | structure of right ovary | ,
424226004 | using device | = 122456005 | laser device | }
{260686004 | method | = 261519002 | diathermy excision - action | ,
    405813007 | procedure site - direct | = 113293009 | structure of left fallopian tube | }""",

    """373873005 |pharmaceutical / biologic product|:
    411116001 |has dose form| = 385049006 |capsule|,
    111115 |active ingredient count| = #1,
    {127489000 |has active ingredient| = 96068000 |amoxicillin trihydrate|,
    111115 |has reference basis of strength| = 372687004 |amoxicillin|,
    111115 |strength magnitude equal to| = #500,  111115 |strength unit| = 258684004 |mg|}""",

    """71388002 |procedure|:
    { 260686004 |method| = 129304002 |excision - action|,
    405813007 |procedure site - direct| = 15497006 |ovarian structure|}
    { 260686004 |method| = 129304002 |excision - action|,
    405813007 |procedure site - direct| = 31435000 |fallopian tube structure|}""",

    """373873005 |pharmaceutical / biologic product|:
    411116001 |has dose form| = 385023001 |oral solution|,
    111115 |active ingredient count| = #1,
    {127489000 |has active ingredient| = 372897005 |albuterol|,
    111115 |has reference basis of strength| = 372897005 |albuterol|,
    111115 |strength magnitude equal to | = #0.083,  111115 |strength unit| = 118582008 |%|}""",

    """322236009 |paracetamol 500 mg tablet|: 111115 |trade name| = "PANADOL" """,

    """373873005 |pharmaceutical / biologic product|:
    411116001 |has dose form| = 385218009 |injection|,
    111115 |active ingredient count| = #2,
    { 127489000 |has active ingredient| = 428126001 |diphtheria toxoid|,
    111115 |has reference basis of strength | = 428126001 |diphtheria toxoid|,
    111115 |strength magnitude minimum| = #4,
    111115 |strength unit| = 259002007 |IU/mL|}
    { 127489000 |has active ingredient| = 412375000 |tetanus toxoid|,
    111115 |has reference basis of strength| = 412375000 |tetanus toxoid|,
    111115 |strength magnitude equal to| = #40,
    111115 |strength unit| = 259002007 |IU/mL|}""",

    """===  46866001 |fracture of lower limb| + 428881005 |injury of tibia|:
    116676008 |associated morphology| = 72704001 |fracture|,
    363698007 |finding site| = 12611008 |bone structure of tibia|""",

    """<<< 73211009 |diabetes mellitus|: 363698007 |finding site| = 113331007 |endocrine system|""",

    """373873005 |pharmaceutical / biologic product|:
    411116001 |has dose form| =
    (421720008 |spray dose form| + 7946007 |drug suspension|)""",

    """397956004 |prosthetic arthroplasty of the hip|:
    363704007 |procedure site| = (24136001 |hip joint structure|:
    272741003 |laterality| = 7771000 |left|)""",

    """397956004 |prosthetic arthroplasty of the hip|:
    363704007 |procedure site| = (24136001 |hip joint structure|:
    272741003 |laterality| = 7771000 |left|),
    { 363699004 |direct device| = 304120007 |total hip replacement prosthesis|,
    260686004 |method| = 257867005 |insertion - action|}""",

    """
243796009 |situation with explicit context|:
{ 408730004 |procedure context| = 385658003 |done|,
  408731000 |temporal context| = 410512000 |current or specified|,
  408732007 |subject relationship context| = 410604004 |subject of record|,
  363589002 |associated procedure| =
( 397956004 |prosthetic arthroplasty of the hip|:
363704007 |procedure site| = (24136001 |hip joint structure|:
272741003 |laterality| = 7771000 |left|)
{ 363699004 |direct device| = 304120007 |total hip replacement prosthesis|,
    260686004 |method| = 257867005 |insertion - action|}) }""",

    """83152002 |oophorectomy|:
    405815000|procedure device| = 122456005 |laser device|""",

    """182201002 |hip joint|:
    272741003 |laterality| = 24028007 |right|""",

    """71388002 |procedure|:
    405815000|procedure device| = 122456005 |laser device|,
    260686004 |method| = 129304002 |excision - action|,
    405813007 |procedure site - direct| = 15497006 |ovarian structure|""",

    """65801008 |excision|:
    405813007 |procedure site - direct| = 66754008 |appendix structure|,
    260870009 |priority| = 25876001 |emergency|""",

    """313056006 |epiphysis of ulna|: 272741003 |laterality| = 7771000 |left|""",

    """119189000 |ulna part| + 312845000 |epiphysis of upper limb|:
    272741003 |laterality| = 7771000 |left|""",

    """421720008 |spray dose form| + 7946007 |drug suspension|""",

    """421720008 + 7946007 |drug suspension|""",

    """421720008
    + 7946007
    |drug suspension|""",

    """73211009 |diabetes mellitus|""",

    """73211009"""
]
