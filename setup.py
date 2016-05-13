#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from pip.req import parse_requirements


requirements = parse_requirements("requirements.txt", session=False)
readme = open('README.md').read()


setup(
    name='crams',
    version='0.1.0',
    description='crams API',
    long_description=readme,
    author='Simon Yu, Melvin Luong, Rafi M feroze',
    author_email='xm.yuau@gmail.com, melvin.luong@monash.edu, mohamed.feroze@monash.edu',
    url='https://github.com/NeCTAR-RC/crams-api',
    packages=find_packages(exclude=['tests', 'local']),
    include_package_data=True,
    install_requires=[str(r.req) for r in requirements],
    license="GPLv3+",
    zip_safe=False,
    keywords='crams',
    platforms='Ubuntu16',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or '
        'later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
    ],
)
