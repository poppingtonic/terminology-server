# coding=utf-8
"""Enumerate the SNOMED files that are in the designated directory"""
__author__ = 'ngurenyaga'

from django.core.exceptions import ValidationError
from django.conf import settings
from pathlib import Path

import os


SNOMED_RELEASE_PATH = Path(os.path.dirname(settings.BASE_DIR) + '/terminology_data')
DELTA_PATH = Path(os.path.dirname(settings.BASE_DIR) + '/terminology_data/delta')
FULL_PATH = Path(os.path.dirname(settings.BASE_DIR) + '/terminology_data/full')


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
        pass

    def _check_clinical_has_international_release():
        """An international release folder should exist in both delta and full"""
        pass

    def _check_drug_has_uk_release():
        """A UK release folder should exist in delta and full"""
        pass

    def _check_all_have_rf2():
        """"Each of the  SIX release folders should have an RF2Release subfolder"""
        pass

    def _check_delta_has_correct_layout():
        """Under RF2Release, there should be 'Delta' then under it 'Refset' and 'Terminology' """
        pass

    def _check_full_has_correct_layout():
        """Under RF2Release, there should be 'Full' then under it 'Refset' and 'Terminology' """
        pass

    def _check_check_release_folder_dates():
        """We should not load content older than what we have in the database"""
        pass

    def _check_release_file_names():
        """Confirm that every release file has a valid name"""
        pass

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
    _check_check_release_folder_dates()
    _check_release_file_names()


def enumerate_full_clinical_release_files(release_type=None):
    """List and categorize the files that are part of a full clinical release

    Return a map of the following format:
    {
      "CONCEPTS": [...list of paths...],
      "DESCRIPTIONS": [...list of paths...],
      ...
    }

    The valid keys are ( in addition to those in the example above ):
        * "RELATIONSHIPS"
        * "SIMPLE_REFERENCE_SET"
        * "ORDERED_REFERENCE_SET"
        * "ATTRIBUTE_VALUE_REFERENCE_SET"
        * "SIMPLE_MAP_REFERENCE_SET"
        * "COMPLEX_MAP_REFERENCE_SET"
        * "EXTENDED_MAP_REFERENCE_SET"
        * "LANGUAGE_REFERENCE_SET"
        * "QUERY_SPECIFICATION_REFERENCE_SET"
        * "ANNOTATION_REFERENCE_SET"
        * "ASSOCIATION_REFERENCE_SET"
        * "MODULE_DEPENDENCY_REFERENCE_SET"
        * "DESCRIPTION_FORMAT_REFERENCE_SET"

    :param release_type:
    """
    # First, validate the release type
    if release_type not in ["FULL_CLINICAL", "FULL_DRUG", "DELTA_CLINICAL", "DELTA_DRUG"]:
        raise ValidationError("Unknown release type")

    # Next, validate the directory layout
    validate_terminology_server_directory_layout()

    # TODO Do the actual dictionary generation
