#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

def readme():
    with open('../README.md') as f:
        return f.read()


setup(
    # PACKAGE
    name='puppet_apis',

    description='Package to access PuppetCa and PuppetDB HTTP APIs for managing certificates and nodes',
    long_description=readme(),
    long_description_content_type='text/markdown',

    version_command='git describe --tags',
    author='SRE Team @leboncoin',
    author_email='opensource@leboncoin.fr',

    url='https://github.com/leboncoin/python-puppet-apis',
    project_urls={
        'Documentation': 'https://pages.github.com/leboncoin/python-puppet-apis',
        'Source': 'https://github.com/leboncoin/python-puppet-apis',
        'Tracker': 'https://github.com/leboncoin/python-puppet-apis/issues',
    },

    # https://choosealicense.com/licenses/mit/
    license='MIT',

    # METADATA
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='puppetserver puppetdb',

    # Setup
    python_requires='>=3',
    install_requires=[
        'requests',
        'certifi',
        # CLI only, hot to not make them as requirements
        'pyopenssl',
        'argparse',
        'configmanager',
        'colorlog',
        'pyyaml'
    ],
    setup_requires=[
        'markdown',
        'pytest-runner',
        'setuptools-version-command'
    ],
    tests_require=[
        'pytest',
        'pytest-docker',
        'pytest-flakes',
        'pytest-pep8'
    ],

    # Directory where is the code
    packages=[
        'puppet_apis'
    ],
    include_package_data=True,
    # https://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation
    entry_points={},
    scripts=['bin/puppet-ca-cli']

)
