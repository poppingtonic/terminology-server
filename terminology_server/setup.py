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
        'Programming Language :: Python :: 3 :: Only',
    ],
    install_requires=[
        'gunicorn==19.6.0',
        'djangorestframework==3.4.4',
        'djangorestframework-camel-case==0.2.0',
        'django-filter==0.15.3',
        'django-cors-headers==1.1.0',
        'django-markdown==0.8.4',
        'dj-database-url==0.4.1',
        'django-extensions==1.7.1',
        'django==1.10',
        'setuptools>=20.9.0',
        'click==6.6',
        'ipython==5.1.0',
        'ipython-genutils==0.1.0',
        'redis==2.10.5',
        'django-redis==4.4.4',
        'google-api-python-client==1.5.1',
        'oauth2client==3.0.0',
        'psycopg2==2.7.4',
        'simplejson>=3.8.2',
        'sarge==0.1.4',
        'stop-words==2015.2.23.1',
        'django-debug-toolbar==1.5',
        'newrelic==2.68.0.50',
        'requests==2.11.0',
        'raven==5.26.0',
        'antlr4-python3-runtime==4.5.3',
        'networkx>=1.11',
        'matplotlib>=2.0.0',
        'pydotplus>=2.0.2'],
    entry_points='''
    [console_scripts]
    termserver=deploy_termserver:instance
    ''',
    scripts=[
        'bin/snomed_manage',
        'bin/run'
    ]
)
