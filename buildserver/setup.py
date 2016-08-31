from setuptools import setup, find_packages
import subprocess

name = 'snomedct-buildserver'

def get_version():
    with open('VERSION') as f:
        version = f.read().strip()

    # Append the Git commit id if this is a development version.
    if version.endswith('+'):
        tag = 'v' + version[:-1]
        try:
            desc = subprocess.check_output([
                'git', 'describe', '--match', tag,
            ])[:-1].decode()
        except Exception:
            version += 'unknown'
        else:
            assert str(desc).startswith(tag)
            import re
            match = re.match(r'v([^-]*)-([0-9]+)-(.*)$', desc)
            if match is None:       # paranoia
                version += 'unknown'
            else:
                ver, rev, local = match.groups()
                version = '%s.post%s+%s' % (ver, rev, local.replace('-', '.'))
                assert '-' not in version

    return version

version = get_version()

setup(
    name=name,
    version=version,
    description="Builds a SNOMED CT terminology server, and deploys it to GCR.",
    url="http://pip.slade360.co.ke/docs/{}/".format(name),
    author="Brian Muhia",
    author_email="bmn@savannahinformatics.com",
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    license="Proprietary",
        classifiers=[
        'Development Status :: 1 - Alpha',
        'Intended Audience :: SIL Developers',
        'Topic :: Software Development :: Infrastructure',
        'Programming Language :: Python :: 2 :: Only',
    ],
    install_requires=[
        'setuptools>=24.0.2',
        'alembic==0.8.5',
        'ansible==2.1.0.0',
        'click==6.6',
        'dropbox==6.1',
        'Flask==0.10.1',
        'Flask-Migrate==1.8.0',
        'Flask-Script==2.0.5',
        'Flask-SQLAlchemy==2.1',
        'google-api-python-client==1.5.1',
        'ipython==5.1.0',
        'ipython-genutils==0.1.0',
        'oauth2client==2.0.1',
        'psycopg2==2.6.2',
        'pytest==2.9.1',
        'SQLAlchemy==1.0.12',
        'sqlalchemy_utils==0.32.1',
        'sqlalchemy-postgres-copy==0.2.0',
        'wrapt==1.10.7',
        'sarge==0.1.4'],
    entry_points='''
    [console_scripts]
    buildserver=commands.snomed_buildserver:instance
    snomed_data=commands.dropbox_content:snomed_data
    load_snomed_data=commands.load_full_release:load_snomed_data
    ''',
    scripts=[
        'manage.py'
    ]
)
