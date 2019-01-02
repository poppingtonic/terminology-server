# coding=utf-8
"""Get the content from a predefined Dropbox folder"""
import os
import re
import json
import logging
import shutil
import zipfile
import dropbox
import click

from itertools import groupby
from urllib3.exceptions import MaxRetryError
from sil_snomed_server.config import config

logging.captureWarnings(True)

# The bulky SNOMED content is kept on DropBox ( too big for GIT )
DROPBOX_SNOMED_FOLDER_URL = os.environ.get("DROPBOX_SNOMED_FOLDER_URL", "")
DROPBOX_APP_KEY = os.environ.get("DROPBOX_APP_KEY", "")
DROPBOX_APP_SECRET = os.environ.get("DROPBOX_APP_SECRET", "")
DROPBOX_ACCESS_TOKEN = os.environ.get("DROPBOX_ACCESS_TOKEN", "")

WORKING_FOLDER = os.path.join(config.basedir, "data/source_terminology_data")
EXTRACT_WORKING_FOLDER = os.path.join(
    config.basedir, "data/extracted_terminology_data"
)
METADATA_FILE = os.path.join(WORKING_FOLDER, "metadata.json")

LOGGER = logging.getLogger(__name__)

# Create the working folders if they do not exist
if not os.path.exists(WORKING_FOLDER):
    os.makedirs(WORKING_FOLDER)
if not os.path.exists(EXTRACT_WORKING_FOLDER):
    os.makedirs(EXTRACT_WORKING_FOLDER)


FILE_PATTERNS = {
    "concepts": re.compile(r"^.*sct2_Concept_.+txt$"),
    "descriptions": re.compile(r"^.*sct2_Description_.+txt$"),
    "relationships": re.compile(r"^.*sct2_Relationship_.+txt$"),
    "text_definitions": re.compile(r"^.*sct2_TextDefinition_.+txt$"),
    "identifiers": re.compile(r"^.*sct2_Identifier_.+txt$"),
    "stated_relationships": re.compile(r"^.*sct2_StatedRelationship_.+txt$"),
    "simple_reference_sets": re.compile(r"^.*der2_.*Refset.+SimpleFull.+txt$"),
    "ordered_reference_sets": re.compile(
        r"^.*der2_.*Refset.+OrderedFull.+txt$"
    ),
    "attribute_value_reference_sets": re.compile(
        r"^.*der2_.*Refset.+AttributeValueFull.+txt$"
    ),
    "simple_map_reference_sets": re.compile(
        r"^.*der2_.*Refset.+SimpleMapFull.+txt$"
    ),
    "complex_map_int_reference_sets": re.compile(
        r"^.*der2_.*Refset.+ComplexMapFull_INT.+txt$"
    ),
    "complex_map_gb_reference_sets": re.compile(
        r"^.*der2_.*Refset.+ComplexMapFull_GB.+txt$"
    ),
    "extended_map_reference_sets": re.compile(
        r"^.*der2_.*Refset.+ExtendedMapFull.+txt$"
    ),
    "language_reference_sets": re.compile(
        r"^.*der2_.*Refset.+LanguageFull.+txt$"
    ),
    "query_specification_reference_sets": re.compile(
        r"^.*der2_.*Refset.+QuerySpecificationFull.+txt$"
    ),
    "annotation_reference_sets": re.compile(
        r"^.*der2_.*Refset.+AnnotationFull.+txt$"
    ),
    "association_reference_sets": re.compile(
        r"^.*der2_.*Refset.+AssociationReferenceFull.+txt$"
    ),
    "module_dependency_reference_sets": re.compile(
        r"^.*der2_.*Refset.+ModuleDependencyFull.+txt$"
    ),
    "description_format_reference_sets": re.compile(
        r"^.*der2_.*Refset.+DescriptionFormatFull.+txt$"
    ),
    "refset_descriptor_reference_sets": re.compile(
        r"^.*der2_.*Refset.*RefsetDescriptorFull.+txt$"
    ),
    "description_type_reference_sets": re.compile(
        r"^.*der2_.*Refset.*DescriptionTypeFull.+txt$"
    ),
}


class DropboxData(object):
    """The SNOMED content is too large to be distributed via GIT"""

    help = "Fetch the current SNOMED content from Dropbox"

    def __init__(self):
        try:
            self.client = dropbox.dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
            self.upstream_metadata = self.client.files_list_folder(
                "/downloads"
            )
            self.stored_metadata = self.get_stored_metadata()
            self.path_keyed_upstream_metadata = [
                {
                    "path": entry.path_display,
                    "server_modified": entry.server_modified.strftime("%c"),
                    "id": entry.id,
                    "rev": entry.rev,
                }
                for entry in self.upstream_metadata.entries
            ]
            self.path_keyed_stored_metadata = self.stored_metadata

            self.has_internet_connection = True
        except MaxRetryError:
            self.has_internet_connection = False

    def get_stored_metadata(self):
        """In a fresh install, it needs to be run twice"""
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE) as f:
                return json.load(f)
        # Default exit
        return None

    def fetch_file(self, file_path):
        """Download the file at file_path ( relative to app's Dropbox root )"""
        # Extract the last part of the filename from the path
        try:
            new_file_name = os.path.basename(file_path)
            new_file_path = os.path.join(WORKING_FOLDER, new_file_name)
            self.client.files_download_to_file(new_file_path, file_path)

            LOGGER.info("Downloaded %s from Dropbox" % new_file_path)
        except:
            LOGGER.info("Unable to fetch %s from Dropbox" % file_path)
            try:
                os.remove(new_file_path)
                LOGGER.info("Deleted %s [ clean up ]" % new_file_path)
            except:
                LOGGER.info("Cannot delete %s [ clean up ]" % new_file_path)

    def save_metadata(self, metadata_dict):
        """Save the newest metadata to file"""
        with open(METADATA_FILE, "w") as f:
            f.write(json.dumps(metadata_dict, indent=4))
        LOGGER.info("Saved metadata")

    def extract_file_paths(self, metadata_dict):
        """Get the file paths of the zipfiles from the metadata dict"""
        if metadata_dict is not []:
            return map(lambda elt: elt["path"], metadata_dict)
        else:
            return []

    def file_has_changed(self, file_path):
        """Return True if a file has changed, otherwise False"""
        LOGGER.debug("Checking if %s has changed" % file_path)
        if file_path not in self.extract_file_paths(
            self.path_keyed_upstream_metadata
        ):
            raise Exception("Inconsistent state; should not occur")

        if file_path not in self.extract_file_paths(
            self.path_keyed_stored_metadata
        ):
            LOGGER.info("%s appears to be a new file" % file_path)
            return True  # We have not seen this file before

        expected_file_path = os.path.join(
            WORKING_FOLDER, os.path.basename(file_path)
        )
        LOGGER.debug("Expected file path: %s" % expected_file_path)
        if not os.path.exists(expected_file_path):
            LOGGER.info("Cannot find expected file %s" % expected_file_path)
            return True

    def metadata_has_changed(self):
        """Return True if there is a change; otherwise False"""
        if not self.stored_metadata:
            LOGGER.info("No stored metadata; assumed to be a new installation")
            return True  # We assume that it is a new installation
        elif os.listdir(EXTRACT_WORKING_FOLDER) == []:
            LOGGER.info(
                "The dest folder - %s - is empty, downloading/extracting"
                % EXTRACT_WORKING_FOLDER
            )
            return True
        else:
            upstream_contents = self.path_keyed_upstream_metadata
            stored_contents = self.path_keyed_stored_metadata
            if len(upstream_contents) != len(stored_contents):
                LOGGER.info("The no of files is different upstream/downstream")
                return True  # There has been a change in the number of files

            for entry in upstream_contents:
                if self.file_has_changed(entry["path"]):
                    LOGGER.info("%s has changed" % entry["path"])
                    return True  # If any file has changed, exit early

        # Default exit
        return False

    def get_upstream_file_paths(self):
        """Produce an iterator of paths to non-dir files upstream"""
        return (entry["path"] for entry in self.path_keyed_upstream_metadata)

    def get_cached_file_paths(self):
        """Produce an iterator of paths to non-dir files in the local folder"""
        # In a fresh install, this will initially have been null
        if not self.stored_metadata:
            self.stored_metadata = self.get_stored_metadata()

        return (entry["path"] for entry in self.path_keyed_stored_metadata)

    def ensure_dest_subfolder_exists(self, subfolder_name):
        """Guarantee that the subfolder exists before we write into it"""
        subfolder_path = os.path.join(EXTRACT_WORKING_FOLDER, subfolder_name)
        if not os.path.exists(subfolder_path):
            os.mkdir(subfolder_path)

        # Confirm that it is a directory
        if not os.path.isdir(subfolder_path):
            raise Exception("%s ought to be a directory" % subfolder_path)

    def save_zip_entry(self, zipfile, zip_entry):
        """Extract the entry to the correct location"""
        release_pattern = re.compile(r"(.*)RF2(.*)/(.*)txt$")
        if zip_entry.endswith(".txt") and release_pattern.match(zip_entry):
            for folder_name, pattern in iter(FILE_PATTERNS.items()):
                self.ensure_dest_subfolder_exists(folder_name)
                if pattern.match(zip_entry):
                    file_name = os.path.basename(zip_entry)
                    subfolder_path = os.path.join(
                        EXTRACT_WORKING_FOLDER, folder_name
                    )
                    item_path = os.path.join(subfolder_path, file_name)
                    with open(item_path, "wb") as dest_file:
                        dest_file.write(zipfile.read(zip_entry))

    def extract_zips(self):
        """(Re-)extract the downloaded SNOMED distribution zipfiles"""
        # Extract zips afresh each time there is a change
        LOGGER.debug("Starting SNOMED zip extraction")
        current_files = os.listdir(EXTRACT_WORKING_FOLDER)
        for current_file in current_files:
            current_path = os.path.join(EXTRACT_WORKING_FOLDER, current_file)
            if not os.path.isdir(current_path):
                os.remove(current_path)
            else:
                shutil.rmtree(current_path, ignore_errors=False)

        source_file_paths = [
            file_path for file_path in self.get_cached_file_paths()
        ]

        for source_file_path in source_file_paths:
            if source_file_path.endswith(".zip"):
                zf = zipfile.ZipFile(
                    WORKING_FOLDER
                    + source_file_path.replace("downloads/", ""),
                    "r",
                )
                entries = zf.namelist()
                for entry in entries:
                    self.save_zip_entry(zf, entry)
        LOGGER.debug("Finished SNOMED zip extraction")


@click.group()
@click.pass_context
def snomed_data(context):
    """Handles the fetching and extraction of SNOMED CT data from Dropbox"""
    context.obj = DropboxData()


@snomed_data.command()
@click.pass_obj
def fetch(dropbox_client):
    """Downloads content from dropbox and extracts it to specific folders"""
    if not dropbox_client.has_internet_connection:
        LOGGER.warning("No internet connection")
        return
    # First, synchronize with Dropbox
    try:
        if dropbox_client.metadata_has_changed():
            # Save the new metadata
            LOGGER.info("Metadata has changed, saving the current state")
            dropbox_client.save_metadata(
                dropbox_client.path_keyed_upstream_metadata
            )

            # SANITY check; there should only be two files in the WORKING_FOLDER
            # folder, until some future date when we start authoring
            # SNOMED content.
            cached_file_paths = list(dropbox_client.get_cached_file_paths())

            assert len(list(cached_file_paths)) == 2

            # 'uk_sct2clfull' should match 1 path
            # 'uk_sct2drfull' should match 1 path
            clinical_path = re.compile(r"^.*uk_sct2cl.+")
            drug_path = re.compile(r"^.*uk_sct2dr.+")

            cached_drug_paths = [
                drug_path.match(file_path)
                for file_path in cached_file_paths
                if drug_path.match(file_path) is not None
            ]

            assert len(cached_drug_paths) == 1

            cached_clinical_paths = [
                clinical_path.match(file_path)
                for file_path in cached_file_paths
                if clinical_path.match(file_path) is not None
            ]

            assert len(cached_clinical_paths) == 1

            LOGGER.info(
                "Correct number of release packages found. Continuing..."
            )

            # Check which files have changed upstream and queue to download
            for upstream_file_path in dropbox_client.get_upstream_file_paths():
                if dropbox_client.file_has_changed(upstream_file_path):
                    LOGGER.info("Fetching %s" % upstream_file_path)
                    dropbox_client.fetch_file(upstream_file_path)

            dropbox_client.extract_zips()
        else:
            LOGGER.info(
                "There is no change in the Dropbox folder. "
                "Happy to do nothing! However, "
                'if your "%s" or "%s" folders are inconsistent, delete '
                "them and re-run this command"
                % (WORKING_FOLDER, EXTRACT_WORKING_FOLDER)
            )
    except MaxRetryError as e:
        LOGGER.warning(
            'UNABLE to reach Dropbox servers: "%s".'
            "We will proceed with the build in the hope that the content "
            "has not changed since the last sync. That hope might be "
            "unwarranted." % e
        )


@snomed_data.command()
def clear():
    """Very unsafe; to be run only to clear space on CircleCI"""
    shutil.rmtree(WORKING_FOLDER, ignore_errors=False)
    shutil.rmtree(EXTRACT_WORKING_FOLDER, ignore_errors=False)


if __name__ == "__main__":
    snomed_data()
