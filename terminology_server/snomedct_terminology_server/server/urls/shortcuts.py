from django.conf.urls import url

from . import views

shortcut_urls = [
    url(r'concepts/diseases/$',
        views.ListDescendants.as_view(),
        {'concept_id': 64572001},
        name='list-diseases'),

    url(r'concepts/symptoms/$',
        views.ListDescendants.as_view(),
        {'concept_id': 418799008},
        name='list-symptoms'),

    url(r'concepts/adverse_reactions/$',
        views.ListDescendants.as_view(),
        {'concept_id': 281647001},
        name='list-adverse-reactions'),

    url(r'concepts/procedures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 71388002},
        name='list-procedures'),

    url(r'concepts/operative_procedures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 387713003},
        name='list-operative-procedures'),

    url(r'concepts/diagnostic_procedures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 103693007},
        name='list-diagnostic-procedures'),

    url(r'concepts/prescriptions/$',
        views.ListDescendants.as_view(),
        {'concept_id': 16076005},
        name='list-prescriptions'),

    url(r'concepts/dispensing_procedures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 440298008},
        name='list-dispensing-procedures'),

    url(r'concepts/drug_regimen_procedures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 182832007},
        name='list-drug-regimen-procedures'),

    url(r'concepts/patient_history/$',
        views.ListDescendants.as_view(),
        {'concept_id': 417662000},
        name='list-patient-history'),

    url(r'concepts/family_history/$',
        views.ListDescendants.as_view(),
        {'concept_id': 416471007},
        name='list-family-history'),

    url(r'concepts/examination_findings/$',
        views.ListDescendants.as_view(),
        {'concept_id': 271906008},
        name='list-examination-findings'),

    url(r'concepts/vital_signs/$',
        views.ListDescendants.as_view(),
        {'concept_id': 46680005},
        name='list-vital-signs'),

    url(r'concepts/evaluation_procedures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 386053000},
        name='list-evaluation-procedures'),

    url(r'concepts/diagnostic_investigations/$',
        views.ListDescendants.as_view(),
        {'concept_id': 306228005},
        name='list-diagnostic-investigations'),

    url(r'concepts/imaging_referrals/$',
        views.ListDescendants.as_view(),
        {'concept_id': 183829003},
        name='list-imaging-referrals'),

    url(r'concepts/investigation_referrals/$',
        views.ListDescendants.as_view(),
        {'concept_id': 281097001},
        name='list-investigation-referrals'),

    url(r'concepts/lab_referrals/$',
        views.ListDescendants.as_view(),
        {'concept_id': 266753000},
        name='list-lab-referrals'),

    url(r'concepts/physiology_referrals/$',
        views.ListDescendants.as_view(),
        {'concept_id': 266754006},
        name='list-physiology-referrals'),

    url(r'concepts/laboratory_procedures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 108252007},
        name='list-laboratory-procedures'),

    url(r'concepts/imaging_procedures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 363679005},
        name='list-imaging-procedures'),

    url(r'concepts/evaluation_findings/$',
        views.ListDescendants.as_view(),
        {'concept_id': 441742003},
        name='list-evaluation-findings'),

    url(r'concepts/imaging_findings/$',
        views.ListDescendants.as_view(),
        {'concept_id': 365853002},
        name='list-imaging-findings'),

    url(r'concepts/specimens/$',
        views.ListDescendants.as_view(),
        {'concept_id': 123038009},
        name='list-specimens'),

    url(r'concepts/assesment_scales/$',
        views.ListDescendants.as_view(),
        {'concept_id': 273249006},
        name='list-assesment-scales'),

    url(r'concepts/chart_procedures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 107727007},
        name='list-chart-procedures'),

    url(r'concepts/administrative_procedures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 14734007},
        name='list-administrative-procedures'),

    url(r'concepts/administrative_procedures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 14734007},
        name='list-administrative-procedures'),

    url(r'concepts/admission_procedures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 305056002},
        name='list-admission-procedures'),

    url(r'concepts/discharge_procedures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 58000006},
        name='list-discharge-procedures'),

    url(r'concepts/body_structures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 123037004},
        name='list-body-structures'),

    url(r'concepts/body_structures/$',
        views.ListDescendants.as_view(),
        {'concept_id': 123037004},
        name='list-body-structures'),

    url(r'concepts/organisms/$',
        views.ListDescendants.as_view(),
        {'concept_id': 410607006},
        name='list-organisms'),

    url(r'concepts/substances/$',
        views.ListDescendants.as_view(),
        {'concept_id': 105590001},
        name='list-substances'),

    url(r'concepts/drugs/$',
        views.ListDescendants.as_view(),
        {'concept_id': 373873005},
        name='list-drugs'),

    url(r'concepts/amps/$',
        views.ListDirectChildren.as_view(),
        {'concept_id': 10363901000001102},
        name='list-amps'),

    url(r'concepts/vmps/$',
        views.ListDirectChildren.as_view(),
        {'concept_id': 10363801000001108},
        name='list-vmps'),

    url(r'concepts/vtms/$',
        views.ListDirectChildren.as_view(),
        {'concept_id': 10363701000001104},
        name='list-vtms'),

    url(r'concepts/vmpps/$',
        views.ListDirectChildren.as_view(),
        {'concept_id': 8653601000001108},
        name='list-vmpps'),

    url(r'concepts/ampps/$',
        views.ListDirectChildren.as_view(),
        {'concept_id': 10364001000001104},
        name='list-ampps'),

    url(r'concepts/search/$',
        views.faceted_search,
        name='raw-faceted-search'),

    url(r'concepts/search/amp/$',
        views.faceted_search,
        {'facet': 'ancestor_ids.amp'},
        name='raw-faceted-search-amp'),

    url(r'concepts/search/vmp/$',
        views.faceted_search,
        {'facet': 'ancestor_ids.vmp'},
        name='raw-faceted-search-vmps'),

    url(r'concepts/search/vtm/$',
        views.faceted_search,
        {'facet': 'parents.vtm'},
        name='raw-faceted-search-vtm'),

    url(r'concepts/search/vmpp/$',
        views.faceted_search,
        {'facet': 'parents.vmpp'},
        name='raw-faceted-search-vmpp'),

    url(r'concepts/search/ampp/$',
        views.faceted_search,
        {'facet': 'parents.ampp'},
        name='raw-faceted-search-ampp'),

    url(r'concepts/search/drugs/$',
        views.faceted_search,
        {'facet': 'ancestor_ids.drugs'},
        name='raw-faceted-search-drugs')
]
