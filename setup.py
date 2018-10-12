#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# import lib
import mblibs

# description
long_description = open('README.md').read()
# long_description += "\n\n"
# long_description += open('CHANGELOG').read()

# setup
setup(
    name='mblibs',
    version=mblibs.__version__,

    packages=find_packages(),

    author="MickBad",
    author_email="prog@mickbad.com",
    description="Fast tools for programming",

    long_description=long_description,
    long_description_content_type='text/markdown',

	install_requires=["pyyaml", "python-dateutil"],

    # activate MANIFEST.in
    include_package_data=True,

    # github source
    url='https://github.com/mickbad/mblibs',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers.
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
    ],

    license="MIT",

    keywords="development tools fasting",
)
