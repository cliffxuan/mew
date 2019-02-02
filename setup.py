#!/usr/bin/env python
import os
import sys

from codecs import open

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

packages = ['mew']

requires = [
    'dataclasses;python_version<"3.7"',
    'pyyaml'
]
dependency_links = [
    # use fork until this RP is approved:
    # https://github.com/ericvsmith/dataclasses/pull/141
    'http://github.com/cliffxuan/dataclasses/tarball/master#egg=dataclasses'
]
test_requirements = [
    'hypothesis',
    'dateutils',
    'flake8',
    'pytest-cov',
    'pytest>=2.8.0'
]

about = {}
with open(os.path.join(here, 'mew', '__version__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=packages,
    package_data={'': ['LICENSE', 'NOTICE']},
    package_dir={'mew': 'mew'},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=requires,
    dependency_links=dependency_links,
    license=about['__license__'],
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    setup_requires=["pytest-runner"],
    tests_require=test_requirements
)
