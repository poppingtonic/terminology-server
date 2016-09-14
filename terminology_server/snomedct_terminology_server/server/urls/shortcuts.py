from django.conf.urls import url
from django.views.decorators.cache import cache_page
from snomedct_terminology_server.config.settings import CACHE_LIFETIME

from . import views

shortcut_urls = [
    url(r'concepts/shortcut/diseases/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 64572001},
        name='list-diseases'),

    url(r'concepts/shortcut/symptoms/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 418799008},
        name='list-symptoms'),

    url(r'concepts/shortcut/adverse_reactions/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 281647001},
        name='list-adverse-reactions'),

    url(r'concepts/shortcut/procedures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 71388002},
        name='list-procedures'),

    url(r'concepts/shortcut/operative_procedures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 387713003},
        name='list-operative-procedures'),

    url(r'concepts/shortcut/diagnostic_procedures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 103693007},
        name='list-diagnostic-procedures'),

    url(r'concepts/shortcut/prescriptions/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 16076005},
        name='list-prescriptions'),

    url(r'concepts/shortcut/dispensing_procedures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 440298008},
        name='list-dispensing-procedures'),

    url(r'concepts/shortcut/drug_regimen_procedures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 182832007},
        name='list-drug-regimen-procedures'),

    url(r'concepts/shortcut/patient_history/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 417662000},
        name='list-patient-history'),

    url(r'concepts/shortcut/family_history/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 416471007},
        name='list-family-history'),

    url(r'concepts/shortcut/examination_findings/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 271906008},
        name='list-examination-findings'),

    url(r'concepts/shortcut/vital_signs/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 46680005},
        name='list-vital-signs'),

    url(r'concepts/shortcut/evaluation_procedures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 386053000},
        name='list-evaluation-procedures'),

    url(r'concepts/shortcut/diagnostic_investigations/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 306228005},
        name='list-diagnostic-investigations'),

    url(r'concepts/shortcut/imaging_referrals/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 183829003},
        name='list-imaging-referrals'),

    url(r'concepts/shortcut/investigation_referrals/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 281097001},
        name='list-investigation-referrals'),

    url(r'concepts/shortcut/lab_referrals/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 266753000},
        name='list-lab-referrals'),

    url(r'concepts/shortcut/physiology_referrals/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 266754006},
        name='list-physiology-referrals'),

    url(r'concepts/shortcut/laboratory_procedures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 108252007},
        name='list-laboratory-procedures'),

    url(r'concepts/shortcut/imaging_procedures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 363679005},
        name='list-imaging-procedures'),

    url(r'concepts/shortcut/evaluation_findings/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 441742003},
        name='list-evaluation-findings'),

    url(r'concepts/shortcut/imaging_findings/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 365853002},
        name='list-imaging-findings'),

    url(r'concepts/shortcut/specimens/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 123038009},
        name='list-specimens'),

    url(r'concepts/shortcut/assesment_scales/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 273249006},
        name='list-assesment-scales'),

    url(r'concepts/shortcut/chart_procedures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 107727007},
        name='list-chart-procedures'),

    url(r'concepts/shortcut/administrative_procedures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 14734007},
        name='list-administrative-procedures'),

    url(r'concepts/shortcut/administrative_procedures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 14734007},
        name='list-administrative-procedures'),

    url(r'concepts/shortcut/admission_procedures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 305056002},
        name='list-admission-procedures'),

    url(r'concepts/shortcut/discharge_procedures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 58000006},
        name='list-discharge-procedures'),

    url(r'concepts/shortcut/body_structures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 123037004},
        name='list-body-structures'),

    url(r'concepts/shortcut/body_structures/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 123037004},
        name='list-body-structures'),

    url(r'concepts/shortcut/organisms/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 410607006},
        name='list-organisms'),

    url(r'concepts/shortcut/substances/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 105590001},
        name='list-substances'),

    url(r'concepts/shortcut/drugs/$',
        cache_page(CACHE_LIFETIME)(views.ListDescendants.as_view()),
        {'concept_id': 410942007},
        name='list-drugs'),

    url(r'concepts/shortcut/amps/$',
        cache_page(CACHE_LIFETIME)(views.ListDirectChildren.as_view()),
        {'concept_id': 10363901000001102},
        name='list-amps'),

    url(r'concepts/shortcut/vmps/$',
        cache_page(CACHE_LIFETIME)(views.ListDirectChildren.as_view()),
        {'concept_id': 10363801000001108},
        name='list-vmps'),

    url(r'concepts/shortcut/vtms/$',
        cache_page(CACHE_LIFETIME)(views.ListDirectChildren.as_view()),
        {'concept_id': 10363701000001104},
        name='list-vtms'),

    url(r'concepts/shortcut/vmpps/$',
        cache_page(CACHE_LIFETIME)(views.ListDirectChildren.as_view()),
        {'concept_id': 8653601000001108},
        name='list-vmpps'),

    url(r'concepts/shortcut/ampps/$',
        cache_page(CACHE_LIFETIME)(views.ListDirectChildren.as_view()),
        {'concept_id': 10364001000001104},
        name='list-ampps')
]
