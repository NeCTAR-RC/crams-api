#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from pip.req import parse_requirements

version = '0.1.0'

readme = open('README.md').read()

requirements = parse_requirements('requirements.txt', session=False)

setup(
    name='crams-db',
    version=version,
    description='crams API',
    long_description=readme,
    author='Rafi M Feroze, Simon Yu',
    author_email='',
    url='https://github.com/NeCTAR-RC/crams-api',
    packages=find_packages(exclude=['tests', 'local']),
    include_package_data=True,
    install_requires=[str(r.req) for r in requirements],
    license='Apache 2.0',
    platforms='Ubuntu16',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Paste',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
    ]
)
