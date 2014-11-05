Extract the SNOMED UK release data into this directory, so that the directory tree ends up looking like this:

The data can be found [on Google Drive](https://doc-0g-2k-docs.googleusercontent.com/docs/securesc/a8th3s8p1p1acr78dbkvhbvrckp6i5d3/aoe7novlofijk2fqp8bs7kc9jf6lopen/1404914400000/07059928310333437090/07059928310333437090/0B7XtbKEY2aI_cUlLYzUxZnU4c0U?e=download&h=04441848913756912604&nonce=6d574a8es3bk8&user=07059928310333437090&hash=qn561sm93jrvocsa45amjm85chr3307q).

```
terminology_data/
├── delta
│   ├── Clinical Extension
│   │   ├── SnomedCT2_GB1000000_20140401
│   │   │   └── RF2Release
│   │   │       └── Delta
│   │   │           ├── Refset
│   │   │           │   ├── Content
│   │   │           │   │   ├── Administrative
│   │   │           │   │   │   └── xder2_icRefset_AdministrativeOrderedDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── CarePlanning
│   │   │           │   │   │   └── der2_Refset_CarePlanningSimpleDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── CareRecordElement
│   │   │           │   │   │   └── der2_Refset_CareRecordElementSimpleDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── ClinicalMessaging
│   │   │           │   │   │   └── xder2_Refset_ClinicalMessagingSimpleDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── der2_cRefset_AssociationReferenceDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── der2_cRefset_AttributeValueDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── DiagnosticImagingProcedure
│   │   │           │   │   │   └── der2_Refset_DiagnosticImagingProcedureSimpleDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── Endoscopy
│   │   │           │   │   │   └── der2_Refset_EndoscopySimpleDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── LinkAssertion
│   │   │           │   │   │   └── xder2_Refset_LinkAssertionSimpleDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── NHSRealmDescription
│   │   │           │   │   │   └── xder2_cRefset_NHSRealmDescriptionLanguageDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── OccupationalTherapy
│   │   │           │   │   │   └── xder2_Refset_OccupationalTherapySimpleDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── PathologyBoundedCodeList
│   │   │           │   │   │   ├── xder2_cRefset_PathologyBoundedCodeListLanguageDelta_GB1000000_20140401.txt
│   │   │           │   │   │   └── xder2_Refset_PathologyBoundedCodeListSimpleDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── PathologyCatalogue
│   │   │           │   │   │   └── xder2_Refset_PathologyCatalogueSimpleDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── ProfessionalRecordStandards
│   │   │           │   │   │   ├── xder2_cRefset_ProfessionalRecordStandardsLanguageDelta_GB1000000_20140401.txt
│   │   │           │   │   │   └── xder2_Refset_ProfessionalRecordStandardsSimpleDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── PublicHealthLanguage
│   │   │           │   │   │   └── xder2_Refset_PublicHealthLanguageSimpleDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── Renal
│   │   │           │   │   │   └── der2_Refset_RenalSimpleDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── SSERP
│   │   │           │   │   │   └── xder2_Refset_SSERPSimpleDelta_GB1000000_20140401.txt
│   │   │           │   │   └── StandardsConsultingGroup
│   │   │           │   │       └── Religions
│   │   │           │   │           ├── xder2_cRefset_ReligionsLanguageDelta_GB1000000_20140401.txt
│   │   │           │   │           └── xder2_Refset_ReligionsSimpleDelta_GB1000000_20140401.txt
│   │   │           │   ├── Crossmap
│   │   │           │   │   ├── der2_sRefset_NHSDataModelandDictionaryAESimpleMapDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── xder2_iisssciRefset_ICD10FourthEditionComplexMapDelta_GB1000000_20140401.txt
│   │   │           │   │   ├── xder2_iisssciRefset_OPCS46ComplexMapDelta_GB1000000_20140401.txt
│   │   │           │   │   └── xder2_iisssciRefset_OPCS47ComplexMapDelta_GB1000000_20140401.txt
│   │   │           │   ├── Language
│   │   │           │   │   └── xder2_cRefset_UKExtensionLanguageDelta-en-GB_GB1000000_20140401.txt
│   │   │           │   └── Metadata
│   │   │           │       ├── der2_cciRefset_RefsetDescriptorDelta_GB1000000_20140401.txt
│   │   │           │       ├── der2_ssRefset_ModuleDependencyDelta_GB1000000_20140401.txt
│   │   │           │       └── xder2_cRefset_MetadataLanguageDelta-en-GB_GB1000000_20140401.txt
│   │   │           └── Terminology
│   │   │               ├── sct2_Concept_Delta_GB1000000_20140401.txt
│   │   │               ├── sct2_Description_Delta-en-GB_GB1000000_20140401.txt
│   │   │               └── sct2_Relationship_Delta_GB1000000_20140401.txt
│   │   └── SnomedCT_Release_INT_20140131
│   │       └── RF2Release
│   │           └── Delta
│   │               ├── Refset
│   │               │   ├── Content
│   │               │   │   ├── der2_cRefset_AssociationReferenceDelta_INT_20140131.txt
│   │               │   │   ├── der2_cRefset_AttributeValueDelta_INT_20140131.txt
│   │               │   │   └── der2_Refset_SimpleDelta_INT_20140131.txt
│   │               │   ├── Language
│   │               │   │   └── der2_cRefset_LanguageDelta-en_INT_20140131.txt
│   │               │   ├── Map
│   │               │   │   ├── der2_iisssccRefset_ExtendedMapDelta_INT_20140131.txt
│   │               │   │   ├── der2_iissscRefset_ComplexMapDelta_INT_20140131.txt
│   │               │   │   └── der2_sRefset_SimpleMapDelta_INT_20140131.txt
│   │               │   └── Metadata
│   │               │       ├── der2_cciRefset_RefsetDescriptorDelta_INT_20140131.txt
│   │               │       ├── der2_ciRefset_DescriptionTypeDelta_INT_20140131.txt
│   │               │       └── der2_ssRefset_ModuleDependencyDelta_INT_20140131.txt
│   │               └── Terminology
│   │                   ├── sct2_Concept_Delta_INT_20140131.txt
│   │                   ├── sct2_Description_Delta-en_INT_20140131.txt
│   │                   ├── sct2_Identifier_Delta_INT_20140131.txt
│   │                   ├── sct2_Relationship_Delta_INT_20140131.txt
│   │                   ├── sct2_StatedRelationship_Delta_INT_20140131.txt
│   │                   └── sct2_TextDefinition_Delta-en_INT_20140131.txt
│   └── Drug Extension
│       └── SnomedCT2_GB1000001_20140528
│           └── RF2Release
│               └── Delta
│                   ├── Refset
│                   │   ├── Content
│                   │   │   ├── ClinicalMessaging
│                   │   │   │   └── der2_Refset_ClinicalMessagingSimpleDelta_GB1000001_20140528.txt
│                   │   │   ├── der2_cRefset_AssociationReferenceDelta_GB1000001_20140528.txt
│                   │   │   ├── der2_cRefset_AttributeValueDelta_GB1000001_20140528.txt
│                   │   │   ├── DMD
│                   │   │   │   ├── der2_cRefset_DMDLanguageDelta_GB1000001_20140528.txt
│                   │   │   │   └── der2_Refset_DMDSimpleDelta_GB1000001_20140528.txt
│                   │   │   ├── Drug
│                   │   │   │   └── xder2_Refset_DrugSimpleDelta_GB1000001_20140528.txt
│                   │   │   ├── EPrescribing
│                   │   │   │   └── xder2_Refset_EPrescribingSimpleDelta_GB1000001_20140528.txt
│                   │   │   └── NHSRealmDescription
│                   │   │       └── xder2_cRefset_NHSRealmDescriptionLanguageDelta_GB1000001_20140528.txt
│                   │   ├── Language
│                   │   │   └── xder2_cRefset_UKDrugExtensionLanguageDelta-en-GB_GB1000001_20140528.txt
│                   │   └── Metadata
│                   │       ├── der2_cciRefset_RefsetDescriptorDelta_GB1000001_20140528.txt
│                   │       ├── der2_ssRefset_ModuleDependencyDelta_GB1000001_20140528.txt
│                   │       └── xder2_cRefset_MetadataLanguageDelta-en-GB_GB1000001_20140528.txt
│                   └── Terminology
│                       ├── sct2_Concept_Delta_GB1000001_20140528.txt
│                       ├── sct2_Description_Delta-en-GB_GB1000001_20140528.txt
│                       └── sct2_Relationship_Delta_GB1000001_20140528.txt
├── full
│   ├── Clinical Extension
│   │   ├── SnomedCT2_GB1000000_20140401
│   │   │   └── RF2Release
│   │   │       └── Full
│   │   │           ├── Refset
│   │   │           │   ├── Content
│   │   │           │   │   ├── Administrative
│   │   │           │   │   │   └── xder2_icRefset_AdministrativeOrderedFull_GB1000000_20140401.txt
│   │   │           │   │   ├── CarePlanning
│   │   │           │   │   │   └── der2_Refset_CarePlanningSimpleFull_GB1000000_20140401.txt
│   │   │           │   │   ├── CareRecordElement
│   │   │           │   │   │   └── der2_Refset_CareRecordElementSimpleFull_GB1000000_20140401.txt
│   │   │           │   │   ├── ClinicalMessaging
│   │   │           │   │   │   └── xder2_Refset_ClinicalMessagingSimpleFull_GB1000000_20140401.txt
│   │   │           │   │   ├── der2_cRefset_AssociationReferenceFull_GB1000000_20140401.txt
│   │   │           │   │   ├── der2_cRefset_AttributeValueFull_GB1000000_20140401.txt
│   │   │           │   │   ├── DiagnosticImagingProcedure
│   │   │           │   │   │   └── der2_Refset_DiagnosticImagingProcedureSimpleFull_GB1000000_20140401.txt
│   │   │           │   │   ├── Endoscopy
│   │   │           │   │   │   └── der2_Refset_EndoscopySimpleFull_GB1000000_20140401.txt
│   │   │           │   │   ├── LinkAssertion
│   │   │           │   │   │   └── xder2_Refset_LinkAssertionSimpleFull_GB1000000_20140401.txt
│   │   │           │   │   ├── NHSRealmDescription
│   │   │           │   │   │   └── xder2_cRefset_NHSRealmDescriptionLanguageFull_GB1000000_20140401.txt
│   │   │           │   │   ├── OccupationalTherapy
│   │   │           │   │   │   └── xder2_Refset_OccupationalTherapySimpleFull_GB1000000_20140401.txt
│   │   │           │   │   ├── PathologyBoundedCodeList
│   │   │           │   │   │   ├── xder2_cRefset_PathologyBoundedCodeListLanguageFull_GB1000000_20140401.txt
│   │   │           │   │   │   └── xder2_Refset_PathologyBoundedCodeListSimpleFull_GB1000000_20140401.txt
│   │   │           │   │   ├── PathologyCatalogue
│   │   │           │   │   │   └── xder2_Refset_PathologyCatalogueSimpleFull_GB1000000_20140401.txt
│   │   │           │   │   ├── ProfessionalRecordStandards
│   │   │           │   │   │   ├── xder2_cRefset_ProfessionalRecordStandardsLanguageFull_GB1000000_20140401.txt
│   │   │           │   │   │   └── xder2_Refset_ProfessionalRecordStandardsSimpleFull_GB1000000_20140401.txt
│   │   │           │   │   ├── PublicHealthLanguage
│   │   │           │   │   │   └── xder2_Refset_PublicHealthLanguageSimpleFull_GB1000000_20140401.txt
│   │   │           │   │   ├── Renal
│   │   │           │   │   │   └── der2_Refset_RenalSimpleFull_GB1000000_20140401.txt
│   │   │           │   │   ├── SSERP
│   │   │           │   │   │   └── xder2_Refset_SSERPSimpleFull_GB1000000_20140401.txt
│   │   │           │   │   └── StandardsConsultingGroup
│   │   │           │   │       └── Religions
│   │   │           │   │           ├── xder2_cRefset_ReligionsLanguageFull_GB1000000_20140401.txt
│   │   │           │   │           └── xder2_Refset_ReligionsSimpleFull_GB1000000_20140401.txt
│   │   │           │   ├── Crossmap
│   │   │           │   │   ├── der2_sRefset_NHSDataModelandDictionaryAESimpleMapFull_GB1000000_20140401.txt
│   │   │           │   │   ├── xder2_iisssciRefset_ICD10FourthEditionComplexMapFull_GB1000000_20140401.txt
│   │   │           │   │   ├── xder2_iisssciRefset_OPCS46ComplexMapFull_GB1000000_20140401.txt
│   │   │           │   │   └── xder2_iisssciRefset_OPCS47ComplexMapFull_GB1000000_20140401.txt
│   │   │           │   ├── Language
│   │   │           │   │   └── xder2_cRefset_UKExtensionLanguageFull-en-GB_GB1000000_20140401.txt
│   │   │           │   └── Metadata
│   │   │           │       ├── der2_cciRefset_RefsetDescriptorFull_GB1000000_20140401.txt
│   │   │           │       ├── der2_ssRefset_ModuleDependencyFull_GB1000000_20140401.txt
│   │   │           │       └── xder2_cRefset_MetadataLanguageFull-en-GB_GB1000000_20140401.txt
│   │   │           └── Terminology
│   │   │               ├── sct2_Concept_Full_GB1000000_20140401.txt
│   │   │               ├── sct2_Description_Full-en-GB_GB1000000_20140401.txt
│   │   │               └── sct2_Relationship_Full_GB1000000_20140401.txt
│   │   └── SnomedCT_Release_INT_20140131
│   │       └── RF2Release
│   │           └── Full
│   │               ├── Refset
│   │               │   ├── Content
│   │               │   │   ├── der2_cRefset_AssociationReferenceFull_INT_20140131.txt
│   │               │   │   ├── der2_cRefset_AttributeValueFull_INT_20140131.txt
│   │               │   │   └── der2_Refset_SimpleFull_INT_20140131.txt
│   │               │   ├── Language
│   │               │   │   └── der2_cRefset_LanguageFull-en_INT_20140131.txt
│   │               │   ├── Map
│   │               │   │   ├── der2_iisssccRefset_ExtendedMapFull_INT_20140131.txt
│   │               │   │   ├── der2_iissscRefset_ComplexMapFull_INT_20140131.txt
│   │               │   │   └── der2_sRefset_SimpleMapFull_INT_20140131.txt
│   │               │   └── Metadata
│   │               │       ├── der2_cciRefset_RefsetDescriptorFull_INT_20140131.txt
│   │               │       ├── der2_ciRefset_DescriptionTypeFull_INT_20140131.txt
│   │               │       └── der2_ssRefset_ModuleDependencyFull_INT_20140131.txt
│   │               └── Terminology
│   │                   ├── sct2_Concept_Full_INT_20140131.txt
│   │                   ├── sct2_Description_Full-en_INT_20140131.txt
│   │                   ├── sct2_Identifier_Full_INT_20140131.txt
│   │                   ├── sct2_Relationship_Full_INT_20140131.txt
│   │                   ├── sct2_StatedRelationship_Full_INT_20140131.txt
│   │                   └── sct2_TextDefinition_Full-en_INT_20140131.txt
│   └── Drug Extension
│       └── SnomedCT2_GB1000001_20140528
│           └── RF2Release
│               └── Full
│                   ├── Refset
│                   │   ├── Content
│                   │   │   ├── ClinicalMessaging
│                   │   │   │   └── der2_Refset_ClinicalMessagingSimpleFull_GB1000001_20140528.txt
│                   │   │   ├── der2_cRefset_AssociationReferenceFull_GB1000001_20140528.txt
│                   │   │   ├── der2_cRefset_AttributeValueFull_GB1000001_20140528.txt
│                   │   │   ├── DMD
│                   │   │   │   ├── der2_cRefset_DMDLanguageFull_GB1000001_20140528.txt
│                   │   │   │   └── der2_Refset_DMDSimpleFull_GB1000001_20140528.txt
│                   │   │   ├── Drug
│                   │   │   │   └── xder2_Refset_DrugSimpleFull_GB1000001_20140528.txt
│                   │   │   ├── EPrescribing
│                   │   │   │   └── xder2_Refset_EPrescribingSimpleFull_GB1000001_20140528.txt
│                   │   │   └── NHSRealmDescription
│                   │   │       └── xder2_cRefset_NHSRealmDescriptionLanguageFull_GB1000001_20140528.txt
│                   │   ├── Language
│                   │   │   └── xder2_cRefset_UKDrugExtensionLanguageFull-en-GB_GB1000001_20140528.txt
│                   │   └── Metadata
│                   │       ├── der2_cciRefset_RefsetDescriptorFull_GB1000001_20140528.txt
│                   │       ├── der2_ssRefset_ModuleDependencyFull_GB1000001_20140528.txt
│                   │       └── xder2_cRefset_MetadataLanguageFull-en-GB_GB1000001_20140528.txt
│                   └── Terminology
│                       ├── sct2_Concept_Full_GB1000001_20140528.txt
│                       ├── sct2_Description_Full-en-GB_GB1000001_20140528.txt
│                       └── sct2_Relationship_Full_GB1000001_20140528.txt
├── README.md
└── zres_WordEquivalents_en-US_INT_20020731.txt

102 directories, 128 files

```
