#!/usr/bin/env python
from setuptools import setup, find_packages
__author__ = 'rolandh'

PRE = "src/idpproxy/metadata/files"
HTDOCS = "%s/mako/htdocs" % PRE
TEMPL = "%s/mako/templates" % PRE
STAT = "%s/static" % PRE
TARGET = "idpproxy/metadata/files"

setup(
    name="idpproxy",
    version="0.2.1",
    description="Proxy between social services and SAML2",
    author="Roland Hedberg",
    author_email="roland.hedberg@adm.umu.se",
    license="Apache 2.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    install_requires=[
        'pysaml2',
        'mako',
        'pycrypto',
        'oic',
    ],
    zip_safe=False,
    data_files=[
        ("%s/mako/htdocs" % TARGET, ["%s/metadata.mako" % HTDOCS,
                                     "%s/metadatasave.mako" % HTDOCS]),
        ("%s/mako/templates" % TARGET, ["%s/root.mako" % TEMPL]),
        ("%s/static" % TARGET, ["%s/style.css" % STAT,
                                "%s/unknown.html" % STAT,
                                "%s/unknownError.html" % STAT])
    ]
)
