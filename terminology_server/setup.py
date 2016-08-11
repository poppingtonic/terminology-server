from setuptools import setup, find_packages
import subprocess

name = 'sil-snomedct-terminology-server'

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
    description="Serves a set of denormalized views of SNOMED CT UK snapshots.",
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
        'gunicorn==19.2.1',
        'djangorestframework==3.4.0',
        'djangorestframework-camel-case==0.2.0',
        'django-filter==0.13.0',
        'django-cors-headers==1.1.0',
        'django-markdown==0.8.4',
        'dj-database-url==0.4.1',
        'django-extensions==1.6.7',
        'django==1.10b1',
        'setuptools>=20.9.0',
        'alembic==0.8.5',
        'click==6.3',
        'ipython==4.2.0',
        'ipython-genutils==0.1.0',
        'redis==2.10.5',
        'django-redis==4.4.3',
        'google-api-python-client==1.5.0',
        'oauth2client==2.0.1',
        'psycopg2==2.6.1',
        'simplejson>=3.8.2',
        'sarge==0.1.4',
        'stop-words==2015.2.23.1',
        'django-debug-toolbar>=1.4',
        'newrelic>=2.66.0',
        'requests==2.10.0'],
    entry_points='''
    [console_scripts]
    termserver=deploy_termserver:instance
    ''',
    scripts=[
        'bin/snomed_manage',
        'bin/run'
    ]
)
