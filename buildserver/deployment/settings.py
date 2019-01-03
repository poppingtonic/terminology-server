"""Environment variables."""
import os
import logging
import pkg_resources

from googleapiclient.discovery import build

# logging
LOGGER = logging.getLogger("SNOMEDBuildServer")
LOGGER.setLevel(logging.DEBUG)
CONSOLE_LOGGER = logging.StreamHandler()
CONSOLE_LOGGER.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
CONSOLE_LOGGER.setFormatter(FORMATTER)
LOGGER.addHandler(CONSOLE_LOGGER)

# compute engine settings
PROJECT = "savannah-emr"
CLIENT_EMAIL = (
    "account-1@savannah-emr.iam.gserviceaccount.com"
)  # service account
SERVICE_ACCOUNT_KEY = os.environ.get("SERVICE_ACCOUNT_KEY")
assert SERVICE_ACCOUNT_KEY, "expected SERVICE_ACCOUNT_KEY to be set"

COMPUTE = build("compute", "v1")
LOGGER.debug(COMPUTE)

# PostgreSQL settings
LOGIN_USER = os.environ.get(
    "SIL_BUILDSERVER_PG_USER", "buildserver_login_user"
)
LOGIN_PASSWORD = os.environ.get(
    "SIL_BUILDSERVER_PG_PASSWORD", "ready+player-one"
)
DB_USER = os.environ.get(
    "SIL_BUILDSERVER_DB_USER", "snomedct_buildserver_user"
)
DB_PASS = os.environ.get("SIL_BUILDSERVER_DB_PASSWORD", "snomedct_buildserver")
DB_NAME = os.environ.get(
    "SIL_BUILDSERVER_DB_NAME", "snomedct_buildserver_backend"
)
TERMSERVER_DB_USER = os.environ.get(
    "SIL_TERMSERVER_DB_USER", "snomedct_termserver_user"
)
TERMSERVER_DB_PASS = os.environ.get(
    "SIL_TERMSERVER_DB_PASSWORD", "snomedct_termserver"
)
TERMSERVER_DB_NAME = os.environ.get(
    "SIL_TERMSERVER_DB_NAME", "snomedct_termserver_backend"
)

# Django settings
SECRET_KEY = os.environ.get("SECRET_KEY")
assert SECRET_KEY, "expected SECRET_KEY to be set"

# Ansible deployment settings
SSH_USER = os.environ.get("USER")
assert SSH_USER, "expected SSH_USER to be set"

BUILDSERVER_VERSION = pkg_resources.require("snomedct-buildserver")[0].version
APP_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
BASE_DIR = os.path.join(APP_DIR, "buildserver")
PRIVATE_KEY = os.environ.get(
    "ANSIBLE_SSH_PRIVATE_KEY_FILE", "~/.ssh/google_compute_engine"
)
BUILDSERVER_CONFIG_FILE = "{}/.buildserver_instance.json".format(BASE_DIR)
BUILDSERVER_PLAYBOOK_FILE = "{}/deployment/snomedct_buildserver.yml".format(
    BASE_DIR
)
DELETE_ON_FAILED_BUILD = False
DELETE_ON_SUCCESSFUL_BUILD = True
HOME = os.environ["HOME"]
