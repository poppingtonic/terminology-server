"""Slade 360 SNOMED Build Server."""
from setuptools import setup, find_packages
import subprocess

name = "snomedct-buildserver"


def get_version():
    """Determine a build server version number."""
    with open("VERSION") as version_file:
        ver = version_file.read().strip()

    # Append the Git commit id if this is a development version.
    if ver.endswith("+"):
        tag = "v" + ver[:-1]
        try:
            desc = subprocess.check_output(
                ["git", "describe", "--match", tag]
            )[:-1].decode()
        except Exception:
            ver += "unknown"
        else:
            assert str(desc).startswith(tag)
            import re

            match = re.match(r"v([^-]*)-([0-9]+)-(.*)$", desc)
            if match is None:  # paranoia
                ver += "unknown"
            else:
                ver, rev, local = match.groups()
                ver = "%s.post%s+%s" % (ver, rev, local.replace("-", "."))
                assert "-" not in ver

    return ver


setup(
    name=name,
    version=get_version(),
    description="Compile (denormalize) UK SNOMED Distribution Data.",
    url="http://pip.slade360.co.ke/docs/{}/".format(name),
    author="Savannah Informatics Developers",
    author_email="emr@savannahinformatics.com",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    license="Proprietary",
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Intended Audience :: SIL Developers",
        "Topic :: Software Development :: Infrastructure",
        "Programming Language :: Python :: 2 :: Only",
    ],
    py_modules=["snomed_buildserver"],
    install_requires=[
        "alembic~=1.0.5",
        "SQLAlchemy~=1.2.15",
        "sqlalchemy_utils~=0.33.10",
        "sqlalchemy-postgres-copy~=0.5.0",
        "ansible~=2.7.5",
        "click~=7.0",
        "sarge~=0.1.5.post0",
        "dropbox~=9.3.0",
        "Flask~=1.0.2",
        "Flask-Migrate~=2.3.0",
        "Flask-Script~=2.0.6",
        "Flask-SQLAlchemy~=2.3.2",
        "google-api-python-client~=1.7.7",
        "ipython~=7.2.0",
        "oauth2client~=4.1.3",
        "psycopg2-binary~=2.7.6.1",
        "pytest~=4.0.2",
        "wrapt~=1.10.11",
    ],
    entry_points="""
    [console_scripts]
    buildserver=snomed_buildserver:instance
    snomed_data=commands.dropbox_content:snomed_data
    load_snomed_data=commands.load_full_release:load_snomed_data
    """,
    scripts=["manage.py"],
)
