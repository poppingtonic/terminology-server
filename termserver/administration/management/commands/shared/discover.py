# coding=utf-8
"""Enumerate the SNOMED files that are in the designated directory"""
__author__ = 'ngurenyaga'

from django.core.exceptions import ValidationError
from django.conf import settings
from pathlib import Path

import os
import re


SNOMED_RELEASE_PATH = Path(os.path.dirname(settings.BASE_DIR) + '/terminology_data')
DELTA_PATH = Path(os.path.dirname(settings.BASE_DIR) + '/terminology_data/delta')
FULL_PATH = Path(os.path.dirname(settings.BASE_DIR) + '/terminology_data/full')
DELTA_CLINICAL_PATH = Path(os.path.dirname(settings.BASE_DIR) + '/terminology_data/delta/Clinical Extension')
FULL_CLINICAL_PATH = Path(os.path.dirname(settings.BASE_DIR) + '/terminology_data/full/Clinical Extension')
DELTA_DRUG_PATH = Path(os.path.dirname(settings.BASE_DIR) + '/terminology_data/delta/Drug Extension')
FULL_DRUG_PATH = Path(os.path.dirname(settings.BASE_DIR) + '/terminology_data/full/Drug Extension')


CLINICAL_RELEASE_REGEX = re.compile('SnomedCT2_GB1000000_\d{8}')  # UK clinical extension release
DRUG_RELEASE_REGEX = re.compile('SnomedCT2_GB1000001_\d{8}')  # UK drug extension release
INTERNATIONAL_RELEASE_REGEX = re.compile('SnomedCT_Release_INT_\d{8}')  # International SNOMED release

# The regular expressions that will be used to validate release file filenames
# They have been obtained from the SNOMED Technical Implementation Guide
FULL_INTERNATIONAL_RELEASE_FILE_REGEX = re.compile(
    r'^x?(sct|der|res)2_[^_]+_[^_]*Full(-[a-z-]{2,6})?_INT_2[0-9]{7}.txt$')
DELTA_INTERNATIONAL_RELEASE_FILE_REGEX = re.compile(
    r'^x?(sct|der|res)2_[^_]+_[^_]*Delta(-[a-z-]{2,6})?_INT_2[0-9]{7}.txt$')
FULL_EXTENSION_RELEASE_FILE_REGEX = re.compile(
    r'^x?(sct|der|res)2_[^_]+_[^_]*Full(-[a-z-]{2,6})?_([A-Z]{2})?[0-9]{7}_2[0-9]{7}.txt$')
DELTA_EXTENSION_RELEASE_FILE_REGEX = re.compile(
    r'^x?(sct|der|res)2_[^_]+_[^_]*Delta(-[a-z-]{2,6})?_([A-Z]{2})?[0-9]{7}_2[0-9]{7}.txt$')
RELEASE_FILE_PATTERNS = [
    FULL_INTERNATIONAL_RELEASE_FILE_REGEX, DELTA_INTERNATIONAL_RELEASE_FILE_REGEX,
    FULL_EXTENSION_RELEASE_FILE_REGEX, DELTA_EXTENSION_RELEASE_FILE_REGEX
]

# The regular expressions used to classify the actual release files
CONCEPT_FILE_REGEX = re.compile(r'^x?sct2_Concept_.+txt$')
DESCRIPTION_FILE_REGEX = re.compile(r'^x?sct2_Description_.+txt$')
RELATIONSHIP_FILE_REGEX = re.compile(r'^x?sct2_Relationship_.+txt$')
SIMPLE_REFERENCE_SET_REGEX = re.compile(r'^x?der2_.+Refset.+Simple.+txt$')
ORDERED_REFERENCE_SET_REGEX = re.compile(r'^x?der2_.+Refset.+Ordered.+txt$')
ATTRIBUTE_VALUE_REFERENCE_SET_REGEX = re.compile(r'^x?der2_.+Refset.+AttributeValue.+txt$')
SIMPLE_MAP_REFERENCE_SET_REGEX = re.compile(r'^x?der2_.+Refset.+SimpleMap.+txt$')
COMPLEX_MAP_REFERENCE_SET_REGEX = re.compile(r'^x?der2_.+Refset.+ComplexMap.+txt$')
EXTENDED_MAP_REFERENCE_SET_REGEX = re.compile(r'^x?der2_.+Refset.+ExtendedMap.+txt$')
LANGUAGE_REFERENCE_SET_REGEX = re.compile(r'^x?der2_.*Refset.+Language.+txt$')
QUERY_SPECIFICATION_REFERENCE_SET_REGEX = re.compile(r'^x?der2_.+Refset.+QuerySpecification.+txt$')
ANNOTATION_REFERENCE_SET_REGEX = re.compile(r'^x?der2_.+Refset.+Annotation.+txt$')
ASSOCIATION_REFERENCE_SET_REGEX = re.compile(r'^x?der2_.+Refset.+Association.+txt$')
MODULE_DEPENDENCY_REFERENCE_SET_REGEX = re.compile(r'^x?der2_.+Refset.+ModuleDependency.+txt$')
DESCRIPTION_FORMAT_REFERENCE_SET_REGEX = re.compile(r'^x?der2_.+Refset.+DescriptionFormat.+txt$')

# The paths to the actual release folders will change with each release, hence the helper functions below
# As implemented, those generators raise a StopIteration error if there is no matching file; it is deliberate
FULL_UK_CLINICAL_RELEASE = next(
    x for x in FULL_CLINICAL_PATH.iterdir() if x.is_dir() and CLINICAL_RELEASE_REGEX.match(x.name))
FULL_INTERNATIONAL_RELEASE = next(
    x for x in FULL_CLINICAL_PATH.iterdir() if x.is_dir() and INTERNATIONAL_RELEASE_REGEX.match(x.name))
FULL_DRUG_RELEASE = next(x for x in FULL_DRUG_PATH.iterdir() if x.is_dir() and DRUG_RELEASE_REGEX.match(x.name))
DELTA_UK_CLINICAL_RELEASE = next(
    x for x in DELTA_CLINICAL_PATH.iterdir() if x.is_dir() and CLINICAL_RELEASE_REGEX.match(x.name))
DELTA_INTERNATIONAL_RELEASE = next(
    x for x in DELTA_CLINICAL_PATH.iterdir() if x.is_dir() and INTERNATIONAL_RELEASE_REGEX.match(x.name))
DELTA_DRUG_RELEASE = next(x for x in DELTA_DRUG_PATH.iterdir() if x.is_dir() and DRUG_RELEASE_REGEX.match(x.name))

ALL_RELEASE_FOLDERS = [
    FULL_UK_CLINICAL_RELEASE, FULL_INTERNATIONAL_RELEASE, FULL_DRUG_RELEASE,
    DELTA_UK_CLINICAL_RELEASE, DELTA_INTERNATIONAL_RELEASE, DELTA_DRUG_RELEASE
]
FULL_RELEASE_FOLDERS = [FULL_UK_CLINICAL_RELEASE, FULL_INTERNATIONAL_RELEASE, FULL_DRUG_RELEASE]
DELTA_RELEASE_FOLDERS = [DELTA_UK_CLINICAL_RELEASE, DELTA_INTERNATIONAL_RELEASE, DELTA_DRUG_RELEASE]


def validate_terminology_server_directory_layout():
    """Sanity checks before we load data from the directory"""

    def _check_terminology_folder_exists():
        """Confirm that the terminology server exists"""
        if not SNOMED_RELEASE_PATH.exists():
            raise ValidationError('The SNOMED content path "%s" does not exist' % SNOMED_RELEASE_PATH)

    def _check_has_delta_and_full_folders():
        """The top level folders should be 'delta' and 'full'"""
        top_level = [x.name for x in SNOMED_RELEASE_PATH.iterdir() if x.is_dir()]
        if not 'delta' in top_level or not 'full' in top_level:
            raise ValidationError('The top level of the terminology data folder should have "delta" and "full"')

    def _check_has_clinical_and_drug_extension_folders():
        """The folders after top should be 'Clinical Extension' and 'Drug Extension'"""
        delta_path_children = [x.name for x in DELTA_PATH.iterdir() if x.is_dir()]
        if not 'Clinical Extension' in delta_path_children or not 'Drug Extension' in delta_path_children:
            raise ValidationError('The delta folder should have "Clinical Extension" and "Drug Extension"')

        full_path_children = [x.name for x in FULL_PATH.iterdir() if x.is_dir()]
        if not 'Clinical Extension' in full_path_children or not 'Drug Extension' in full_path_children:
            raise ValidationError('The full release folder should have "Clinical Extension" and "Drug Extension"')

    def _check_clinical_has_uk_release():
        """A UK clinical release folder should exist in both delta and full"""
        delta_clinical_children = [x.name for x in DELTA_CLINICAL_PATH.iterdir() if x.is_dir()]
        if not any(CLINICAL_RELEASE_REGEX.match(s) for s in delta_clinical_children):
            raise ValidationError('There should be a UK release in the delta clinical extension folder')

        full_clinical_children = [x.name for x in FULL_CLINICAL_PATH.iterdir() if x.is_dir()]
        if not any(CLINICAL_RELEASE_REGEX.match(s) for s in full_clinical_children):
            raise ValidationError('There should be an international release in the full clinical extension folder')

    def _check_clinical_has_international_release():
        """An international release folder should exist in both delta and full"""
        delta_clinical_children = [x.name for x in DELTA_CLINICAL_PATH.iterdir() if x.is_dir()]
        if not any(INTERNATIONAL_RELEASE_REGEX.match(s) for s in delta_clinical_children):
            raise ValidationError('There should be a UK release in the delta clinical extension folder')

        full_clinical_children = [x.name for x in FULL_CLINICAL_PATH.iterdir() if x.is_dir()]
        if not any(INTERNATIONAL_RELEASE_REGEX.match(s) for s in full_clinical_children):
            raise ValidationError('There should be an international release in the full clinical extension folder')

    def _check_drug_has_uk_release():
        """A UK release folder should exist in delta and full"""
        delta_drug_children = [x.name for x in DELTA_DRUG_PATH.iterdir() if x.is_dir()]
        if not any(DRUG_RELEASE_REGEX.match(s) for s in delta_drug_children):
            raise ValidationError('There should be a UK release in the delta drug extension folder')

        full_drug_children = [x.name for x in FULL_DRUG_PATH.iterdir() if x.is_dir()]
        if not any(DRUG_RELEASE_REGEX.match(s) for s in full_drug_children):
            raise ValidationError('There should be a UK release in the full drug extension folder')

    def _check_all_have_rf2():
        """"Each of the  SIX release folders should have an RF2Release subfolder"""
        if not any(("RF2Release" in [x.name for x in folder.iterdir() if x.is_dir()]) for folder in ALL_RELEASE_FOLDERS):
            raise ValidationError("Every release folder must have an Rf2Release sub-folder")

    def _check_delta_has_correct_layout():
        """Under RF2Release, there should be 'Delta' then under it 'Refset' and 'Terminology' """
        for folder in [delta_folder / "RF2Release" for delta_folder in DELTA_RELEASE_FOLDERS]:
            # Should have a "Delta" subdirectory
            folder_subdir_names = [x.name for x in folder.iterdir() if x.is_dir()]
            if "Delta" not in folder_subdir_names:
                raise ValidationError('Missing "delta" folder in %s' % folder)
            # The "delta" subdirectory should contain "Refset" and "Terminology"
            folder_subdirs = [x for x in folder.iterdir() if x.is_dir()]
            if any("Refset" not in [x.name for x in f.iterdir() if x.is_dir()] for f in folder_subdirs):
                raise ValidationError('Missing "refset" folder in %s/delta' % folder)

            if any("Terminology" not in [x.name for x in f.iterdir() if x.is_dir()] for f in folder_subdirs):
                raise ValidationError('Missing "refset" folder in %s/delta' % folder)

    def _check_full_has_correct_layout():
        """Under RF2Release, there should be 'Full' then under it 'Refset' and 'Terminology' """
        for folder in [full_folder / "RF2Release" for full_folder in FULL_RELEASE_FOLDERS]:
            # Should have a "Full" subdirectory
            folder_subdir_names = [x.name for x in folder.iterdir() if x.is_dir()]
            if "Full" not in folder_subdir_names:
                raise ValidationError('Missing "full" folder in %s' % folder)
            # The "full" subdirectory should contain "Refset" and "Terminology"
            folder_subdirs = [x for x in folder.iterdir() if x.is_dir()]
            if any("Refset" not in [x.name for x in f.iterdir() if x.is_dir()] for f in folder_subdirs):
                raise ValidationError('Missing "refset" folder in %s/full' % folder)

            if any("Terminology" not in [x.name for x in f.iterdir() if x.is_dir()] for f in folder_subdirs):
                raise ValidationError('Missing "refset" folder in %s/full' % folder)

    def _check_release_file_names():
        """Confirm that every release file has a valid name"""
        # First, enumerate all release files
        release_files = [path.name for path in SNOMED_RELEASE_PATH.glob('**/*.txt')]

        # Check that each file matches at least one regex
        for release_file in release_files:
            if not any(regex.match(release_file) for regex in RELEASE_FILE_PATTERNS):
                raise ValidationError('"%s" does not match any expected release file pattern' % release_file)

        # Next, that none exceeds 128 characters
        for release_file in release_files:
            if len(release_file) > 128:
                raise ValidationError('"%s" is longer than 128 characters' % release_file)

    # Put it all together
    _check_terminology_folder_exists()
    _check_has_delta_and_full_folders()
    _check_has_clinical_and_drug_extension_folders()
    _check_clinical_has_uk_release()
    _check_clinical_has_international_release()
    _check_drug_has_uk_release()
    _check_all_have_rf2()
    _check_delta_has_correct_layout()
    _check_full_has_correct_layout()
    _check_release_file_names()


def enumerate_release_files(release_type=None):
    """List and categorize the files that are part of a full clinical release

    Return a map in the format specified by return_dict

    :param release_type:
    """
    return_dict = {
        "CONCEPTS": [],
        "DESCRIPTIONS": [],
        "RELATIONSHIPS": [],
        "SIMPLE_REFERENCE_SET": [],
        "ORDERED_REFERENCE_SET": [],
        "ATTRIBUTE_VALUE_REFERENCE_SET": [],
        "SIMPLE_MAP_REFERENCE_SET": [],
        "COMPLEX_MAP_REFERENCE_SET": [],
        "EXTENDED_MAP_REFERENCE_SET": [],
        "LANGUAGE_REFERENCE_SET": [],
        "QUERY_SPECIFICATION_REFERENCE_SET": [],
        "ANNOTATION_REFERENCE_SET": [],
        "ASSOCIATION_REFERENCE_SET": [],
        "MODULE_DEPENDENCY_REFERENCE_SET": [],
        "DESCRIPTION_FORMAT_REFERENCE_SET": []
    }

    def _classify(path_list):
        """The actual work occurs here"""
        for path in path_list:
            if CONCEPT_FILE_REGEX.match(path.name):
                return_dict["CONCEPTS"].append(path)
            elif DESCRIPTION_FILE_REGEX.match(path.name):
                return_dict["DESCRIPTIONS"].append(path)
            elif RELATIONSHIP_FILE_REGEX.match(path.name):
                return_dict["RELATIONSHIPS"].append(path)
            elif SIMPLE_REFERENCE_SET_REGEX.match(path.name):
                return_dict["SIMPLE_REFERENCE_SET"].append(path)
            elif ORDERED_REFERENCE_SET_REGEX.match(path.name):
                return_dict["ORDERED_REFERENCE_SET"].append(path)
            elif ATTRIBUTE_VALUE_REFERENCE_SET_REGEX.match(path.name):
                return_dict["ATTRIBUTE_VALUE_REFERENCE_SET"].append(path)
            elif SIMPLE_MAP_REFERENCE_SET_REGEX.match(path.name):
                return_dict["SIMPLE_MAP_REFERENCE_SET"].append(path)
            elif COMPLEX_MAP_REFERENCE_SET_REGEX.match(path.name):
                return_dict["COMPLEX_MAP_REFERENCE_SET"].append(path)
            elif EXTENDED_MAP_REFERENCE_SET_REGEX.match(path.name):
                return_dict["EXTENDED_MAP_REFERENCE_SET"].append(path)
            elif LANGUAGE_REFERENCE_SET_REGEX.match(path.name):
                return_dict["LANGUAGE_REFERENCE_SET"].append(path)
            elif QUERY_SPECIFICATION_REFERENCE_SET_REGEX.match(path.name):
                return_dict["QUERY_SPECIFICATION_REFERENCE_SET"].append(path)
            elif ANNOTATION_REFERENCE_SET_REGEX.match(path.name):
                return_dict["ANNOTATION_REFERENCE_SET"].append(path)
            elif ASSOCIATION_REFERENCE_SET_REGEX.match(path.name):
                return_dict["ASSOCIATION_REFERENCE_SET"].append(path)
            elif MODULE_DEPENDENCY_REFERENCE_SET_REGEX.match(path.name):
                return_dict["MODULE_DEPENDENCY_REFERENCE_SET"].append(path)
            elif DESCRIPTION_FORMAT_REFERENCE_SET_REGEX.match(path.name):
                return_dict["DESCRIPTION_FORMAT_REFERENCE_SET"].append(path)
            else:
                raise ValidationError('Unexpected file type "%s"' % path)
        return return_dict

    # Validate the directory layout, then list and classify the content files
    validate_terminology_server_directory_layout()
    if release_type == "FULL_CLINICAL":
        return _classify(FULL_CLINICAL_PATH.glob('**/*.txt'))
    elif release_type == "FULL_DRUG":
        return _classify(FULL_DRUG_PATH.glob('**/*.txt'))
    elif release_type == "DELTA_CLINICAL":
        return _classify(DELTA_CLINICAL_PATH.glob('**/*.txt'))
    elif release_type == "DELTA_DRUG":
        return _classify(DELTA_DRUG_PATH.glob('**/*.txt'))
    else:
        raise ValidationError("Unknown release type")
