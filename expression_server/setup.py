from setuptools import setup, find_packages
import subprocess

name = 'snomedct-expression-server'


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
    description="Understands SNOMED CT expressions",
    url="http://pip.slade360.co.ke/docs/{}/".format(name),
    author="Brian Muhia",
    author_email="bmn@savannahinformatics.com",
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    license="Proprietary",
        classifiers=[
        'Development Status :: 0 - Pre-Alpha',
        'Intended Audience :: SIL Developers',
        'Topic :: Software Development :: Infrastructure',
        'Programming Language :: Python :: 3 :: Only',
    ],
    install_requires=['antlr4-python3-runtime'],
    scripts=[
        'bin/pygrun'
    ]
)
