This server contains five Django apps:

 * `administration` - administrative utilities, including the loading and updating commands
 * `authoring` - services that will be used to add new content
 * `core` - storage and manipulation of the core SNOMED **components**
 * `refset` - storage and manipulation of extension ( reference set ) content
 * `search` - search index creation and maintenance, search APIs\
 
SNOMED Data Directory Structure
=================================
Our base dataset is the UK Clinical and Drugs releases. There is a `uk-terminology-data`
folder in this repository's root directory. 

The data should be added to that folder in the **prepared in the manner shown below**:
 * all documentation files deleted
 * all support resources deleted
 * all RF1 content deleted
 
For initial loads and reconstructions, the "full" content will be used. For updates e.g the 
fortnightly drug release updates, the "delta" content will be used.

```
uk-terminology-data/
├- delta
|   ├- Clinical Extension
|   |   ├- SnomedCT2-GB1000000-20140401
|   |   |   |- RF2Release
|   |   |       |- Delta
|   |   |           ├- Refset
|   |   |           |   ├- Content
|   |   |           |   |   ├- Administrative
|   |   |           |   |   |   |- xder2-icRefset-AdministrativeOrderedDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- CarePlanning
|   |   |           |   |   |   |- der2-Refset-CarePlanningSimpleDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- CareRecordElement
|   |   |           |   |   |   |- der2-Refset-CareRecordElementSimpleDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- ClinicalMessaging
|   |   |           |   |   |   |- xder2-Refset-ClinicalMessagingSimpleDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- der2-cRefset-AssociationReferenceDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- der2-cRefset-AttributeValueDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- DiagnosticImagingProcedure
|   |   |           |   |   |   |- der2-Refset-DiagnosticImagingProcedureSimpleDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- Endoscopy
|   |   |           |   |   |   |- der2-Refset-EndoscopySimpleDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- LinkAssertion
|   |   |           |   |   |   |- xder2-Refset-LinkAssertionSimpleDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- NHSRealmDescription
|   |   |           |   |   |   |- xder2-cRefset-NHSRealmDescriptionLanguageDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- OccupationalTherapy
|   |   |           |   |   |   |- xder2-Refset-OccupationalTherapySimpleDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- PathologyBoundedCodeList
|   |   |           |   |   |   ├- xder2-cRefset-PathologyBoundedCodeListLanguageDelta-GB1000000-20140401.txt
|   |   |           |   |   |   |- xder2-Refset-PathologyBoundedCodeListSimpleDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- PathologyCatalogue
|   |   |           |   |   |   |- xder2-Refset-PathologyCatalogueSimpleDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- ProfessionalRecordStandards
|   |   |           |   |   |   ├- xder2-cRefset-ProfessionalRecordStandardsLanguageDelta-GB1000000-20140401.txt
|   |   |           |   |   |   |- xder2-Refset-ProfessionalRecordStandardsSimpleDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- PublicHealthLanguage
|   |   |           |   |   |   |- xder2-Refset-PublicHealthLanguageSimpleDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- Renal
|   |   |           |   |   |   |- der2-Refset-RenalSimpleDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- SSERP
|   |   |           |   |   |   |- xder2-Refset-SSERPSimpleDelta-GB1000000-20140401.txt
|   |   |           |   |   |- StandardsConsultingGroup
|   |   |           |   |       |- Religions
|   |   |           |   |           ├- xder2-cRefset-ReligionsLanguageDelta-GB1000000-20140401.txt
|   |   |           |   |           |- xder2-Refset-ReligionsSimpleDelta-GB1000000-20140401.txt
|   |   |           |   ├- Crossmap
|   |   |           |   |   ├- der2-sRefset-NHSDataModelandDictionaryAESimpleMapDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- xder2-iisssciRefset-ICD10FourthEditionComplexMapDelta-GB1000000-20140401.txt
|   |   |           |   |   ├- xder2-iisssciRefset-OPCS46ComplexMapDelta-GB1000000-20140401.txt
|   |   |           |   |   |- xder2-iisssciRefset-OPCS47ComplexMapDelta-GB1000000-20140401.txt
|   |   |           |   ├- Language
|   |   |           |   |   |- xder2-cRefset-UKExtensionLanguageDelta-en-GB-GB1000000-20140401.txt
|   |   |           |   |- Metadata
|   |   |           |       ├- der2-cciRefset-RefsetDescriptorDelta-GB1000000-20140401.txt
|   |   |           |       ├- der2-ssRefset-ModuleDependencyDelta-GB1000000-20140401.txt
|   |   |           |       |- xder2-cRefset-MetadataLanguageDelta-en-GB-GB1000000-20140401.txt
|   |   |           |- Terminology
|   |   |               ├- sct2-Concept-Delta-GB1000000-20140401.txt
|   |   |               ├- sct2-Description-Delta-en-GB-GB1000000-20140401.txt
|   |   |               |- sct2-Relationship-Delta-GB1000000-20140401.txt
|   |   |- SnomedCT-Release-INT-20140131
|   |       |- RF2Release
|   |           |- Delta
|   |               ├- Refset
|   |               |   ├- Content
|   |               |   |   ├- der2-cRefset-AssociationReferenceDelta-INT-20140131.txt
|   |               |   |   ├- der2-cRefset-AttributeValueDelta-INT-20140131.txt
|   |               |   |   |- der2-Refset-SimpleDelta-INT-20140131.txt
|   |               |   ├- Language
|   |               |   |   |- der2-cRefset-LanguageDelta-en-INT-20140131.txt
|   |               |   ├- Map
|   |               |   |   ├- der2-iisssccRefset-ExtendedMapDelta-INT-20140131.txt
|   |               |   |   ├- der2-iissscRefset-ComplexMapDelta-INT-20140131.txt
|   |               |   |   |- der2-sRefset-SimpleMapDelta-INT-20140131.txt
|   |               |   |- Metadata
|   |               |       ├- der2-cciRefset-RefsetDescriptorDelta-INT-20140131.txt
|   |               |       ├- der2-ciRefset-DescriptionTypeDelta-INT-20140131.txt
|   |               |       |- der2-ssRefset-ModuleDependencyDelta-INT-20140131.txt
|   |               |- Terminology
|   |                   ├- sct2-Concept-Delta-INT-20140131.txt
|   |                   ├- sct2-Description-Delta-en-INT-20140131.txt
|   |                   ├- sct2-Identifier-Delta-INT-20140131.txt
|   |                   ├- sct2-Relationship-Delta-INT-20140131.txt
|   |                   ├- sct2-StatedRelationship-Delta-INT-20140131.txt
|   |                   |- sct2-TextDefinition-Delta-en-INT-20140131.txt
|   |- Drug Extension
|       |- SnomedCT2-GB1000001-20140528
|           |- RF2Release
|               |- Delta
|                   ├- Refset
|                   |   ├- Content
|                   |   |   ├- ClinicalMessaging
|                   |   |   |   |- der2-Refset-ClinicalMessagingSimpleDelta-GB1000001-20140528.txt
|                   |   |   ├- der2-cRefset-AssociationReferenceDelta-GB1000001-20140528.txt
|                   |   |   ├- der2-cRefset-AttributeValueDelta-GB1000001-20140528.txt
|                   |   |   ├- DMD
|                   |   |   |   ├- der2-cRefset-DMDLanguageDelta-GB1000001-20140528.txt
|                   |   |   |   |- der2-Refset-DMDSimpleDelta-GB1000001-20140528.txt
|                   |   |   ├- Drug
|                   |   |   |   |- xder2-Refset-DrugSimpleDelta-GB1000001-20140528.txt
|                   |   |   ├- EPrescribing
|                   |   |   |   |- xder2-Refset-EPrescribingSimpleDelta-GB1000001-20140528.txt
|                   |   |   |- NHSRealmDescription
|                   |   |       |- xder2-cRefset-NHSRealmDescriptionLanguageDelta-GB1000001-20140528.txt
|                   |   ├- Language
|                   |   |   |- xder2-cRefset-UKDrugExtensionLanguageDelta-en-GB-GB1000001-20140528.txt
|                   |   |- Metadata
|                   |       ├- der2-cciRefset-RefsetDescriptorDelta-GB1000001-20140528.txt
|                   |       ├- der2-ssRefset-ModuleDependencyDelta-GB1000001-20140528.txt
|                   |       |- xder2-cRefset-MetadataLanguageDelta-en-GB-GB1000001-20140528.txt
|                   |- Terminology
|                       ├- sct2-Concept-Delta-GB1000001-20140528.txt
|                       ├- sct2-Description-Delta-en-GB-GB1000001-20140528.txt
|                       |- sct2-Relationship-Delta-GB1000001-20140528.txt
|- full
    ├- Clinical Extension
    |   ├- SnomedCT2-GB1000000-20140401
    |   |   |- RF2Release
    |   |       |- Full
    |   |           ├- Refset
    |   |           |   ├- Content
    |   |           |   |   ├- Administrative
    |   |           |   |   |   |- xder2-icRefset-AdministrativeOrderedFull-GB1000000-20140401.txt
    |   |           |   |   ├- CarePlanning
    |   |           |   |   |   |- der2-Refset-CarePlanningSimpleFull-GB1000000-20140401.txt
    |   |           |   |   ├- CareRecordElement
    |   |           |   |   |   |- der2-Refset-CareRecordElementSimpleFull-GB1000000-20140401.txt
    |   |           |   |   ├- ClinicalMessaging
    |   |           |   |   |   |- xder2-Refset-ClinicalMessagingSimpleFull-GB1000000-20140401.txt
    |   |           |   |   ├- der2-cRefset-AssociationReferenceFull-GB1000000-20140401.txt
    |   |           |   |   ├- der2-cRefset-AttributeValueFull-GB1000000-20140401.txt
    |   |           |   |   ├- DiagnosticImagingProcedure
    |   |           |   |   |   |- der2-Refset-DiagnosticImagingProcedureSimpleFull-GB1000000-20140401.txt
    |   |           |   |   ├- Endoscopy
    |   |           |   |   |   |- der2-Refset-EndoscopySimpleFull-GB1000000-20140401.txt
    |   |           |   |   ├- LinkAssertion
    |   |           |   |   |   |- xder2-Refset-LinkAssertionSimpleFull-GB1000000-20140401.txt
    |   |           |   |   ├- NHSRealmDescription
    |   |           |   |   |   |- xder2-cRefset-NHSRealmDescriptionLanguageFull-GB1000000-20140401.txt
    |   |           |   |   ├- OccupationalTherapy
    |   |           |   |   |   |- xder2-Refset-OccupationalTherapySimpleFull-GB1000000-20140401.txt
    |   |           |   |   ├- PathologyBoundedCodeList
    |   |           |   |   |   ├- xder2-cRefset-PathologyBoundedCodeListLanguageFull-GB1000000-20140401.txt
    |   |           |   |   |   |- xder2-Refset-PathologyBoundedCodeListSimpleFull-GB1000000-20140401.txt
    |   |           |   |   ├- PathologyCatalogue
    |   |           |   |   |   |- xder2-Refset-PathologyCatalogueSimpleFull-GB1000000-20140401.txt
    |   |           |   |   ├- ProfessionalRecordStandards
    |   |           |   |   |   ├- xder2-cRefset-ProfessionalRecordStandardsLanguageFull-GB1000000-20140401.txt
    |   |           |   |   |   |- xder2-Refset-ProfessionalRecordStandardsSimpleFull-GB1000000-20140401.txt
    |   |           |   |   ├- PublicHealthLanguage
    |   |           |   |   |   |- xder2-Refset-PublicHealthLanguageSimpleFull-GB1000000-20140401.txt
    |   |           |   |   ├- Renal
    |   |           |   |   |   |- der2-Refset-RenalSimpleFull-GB1000000-20140401.txt
    |   |           |   |   ├- SSERP
    |   |           |   |   |   |- xder2-Refset-SSERPSimpleFull-GB1000000-20140401.txt
    |   |           |   |   |- StandardsConsultingGroup
    |   |           |   |       |- Religions
    |   |           |   |           ├- xder2-cRefset-ReligionsLanguageFull-GB1000000-20140401.txt
    |   |           |   |           |- xder2-Refset-ReligionsSimpleFull-GB1000000-20140401.txt
    |   |           |   ├- Crossmap
    |   |           |   |   ├- der2-sRefset-NHSDataModelandDictionaryAESimpleMapFull-GB1000000-20140401.txt
    |   |           |   |   ├- xder2-iisssciRefset-ICD10FourthEditionComplexMapFull-GB1000000-20140401.txt
    |   |           |   |   ├- xder2-iisssciRefset-OPCS46ComplexMapFull-GB1000000-20140401.txt
    |   |           |   |   |- xder2-iisssciRefset-OPCS47ComplexMapFull-GB1000000-20140401.txt
    |   |           |   ├- Language
    |   |           |   |   |- xder2-cRefset-UKExtensionLanguageFull-en-GB-GB1000000-20140401.txt
    |   |           |   |- Metadata
    |   |           |       ├- der2-cciRefset-RefsetDescriptorFull-GB1000000-20140401.txt
    |   |           |       ├- der2-ssRefset-ModuleDependencyFull-GB1000000-20140401.txt
    |   |           |       |- xder2-cRefset-MetadataLanguageFull-en-GB-GB1000000-20140401.txt
    |   |           |- Terminology
    |   |               ├- sct2-Concept-Full-GB1000000-20140401.txt
    |   |               ├- sct2-Description-Full-en-GB-GB1000000-20140401.txt
    |   |               |- sct2-Relationship-Full-GB1000000-20140401.txt
    |   |- SnomedCT-Release-INT-20140131
    |       |- RF2Release
    |           |- Full
    |               ├- Refset
    |               |   ├- Content
    |               |   |   ├- der2-cRefset-AssociationReferenceFull-INT-20140131.txt
    |               |   |   ├- der2-cRefset-AttributeValueFull-INT-20140131.txt
    |               |   |   |- der2-Refset-SimpleFull-INT-20140131.txt
    |               |   ├- Language
    |               |   |   |- der2-cRefset-LanguageFull-en-INT-20140131.txt
    |               |   ├- Map
    |               |   |   ├- der2-iisssccRefset-ExtendedMapFull-INT-20140131.txt
    |               |   |   ├- der2-iissscRefset-ComplexMapFull-INT-20140131.txt
    |               |   |   |- der2-sRefset-SimpleMapFull-INT-20140131.txt
    |               |   |- Metadata
    |               |       ├- der2-cciRefset-RefsetDescriptorFull-INT-20140131.txt
    |               |       ├- der2-ciRefset-DescriptionTypeFull-INT-20140131.txt
    |               |       |- der2-ssRefset-ModuleDependencyFull-INT-20140131.txt
    |               |- Terminology
    |                   ├- sct2-Concept-Full-INT-20140131.txt
    |                   ├- sct2-Description-Full-en-INT-20140131.txt
    |                   ├- sct2-Identifier-Full-INT-20140131.txt
    |                   ├- sct2-Relationship-Full-INT-20140131.txt
    |                   ├- sct2-StatedRelationship-Full-INT-20140131.txt
    |                   |- sct2-TextDefinition-Full-en-INT-20140131.txt
    |- Drug Extension
        |- SnomedCT2-GB1000001-20140528
            |- RF2Release
                |- Full
                    ├- Refset
                    |   ├- Content
                    |   |   ├- ClinicalMessaging
                    |   |   |   |- der2-Refset-ClinicalMessagingSimpleFull-GB1000001-20140528.txt
                    |   |   ├- der2-cRefset-AssociationReferenceFull-GB1000001-20140528.txt
                    |   |   ├- der2-cRefset-AttributeValueFull-GB1000001-20140528.txt
                    |   |   ├- DMD
                    |   |   |   ├- der2-cRefset-DMDLanguageFull-GB1000001-20140528.txt
                    |   |   |   |- der2-Refset-DMDSimpleFull-GB1000001-20140528.txt
                    |   |   ├- Drug
                    |   |   |   |- xder2-Refset-DrugSimpleFull-GB1000001-20140528.txt
                    |   |   ├- EPrescribing
                    |   |   |   |- xder2-Refset-EPrescribingSimpleFull-GB1000001-20140528.txt
                    |   |   |- NHSRealmDescription
                    |   |       |- xder2-cRefset-NHSRealmDescriptionLanguageFull-GB1000001-20140528.txt
                    |   ├- Language
                    |   |   |- xder2-cRefset-UKDrugExtensionLanguageFull-en-GB-GB1000001-20140528.txt
                    |   |- Metadata
                    |       ├- der2-cciRefset-RefsetDescriptorFull-GB1000001-20140528.txt
                    |       ├- der2-ssRefset-ModuleDependencyFull-GB1000001-20140528.txt
                    |       |- xder2-cRefset-MetadataLanguageFull-en-GB-GB1000001-20140528.txt
                    |- Terminology
                        ├- sct2-Concept-Full-GB1000001-20140528.txt
                        ├- sct2-Description-Full-en-GB-GB1000001-20140528.txt
                        |- sct2-Relationship-Full-GB1000001-20140528.txt

102 directories, 126 files
```
