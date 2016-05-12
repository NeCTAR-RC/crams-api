#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

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
    install_requires=[
                      'astroid==1.4.4',
                      'autopep8==1.2.2',
                      'Babel==1.3',
                      'colorama==0.3.6',
                      'coverage==4.0.3',
                      'debtcollector==1.1.0',
                      'Django==1.8.7',
                      'django-babel==0.3.9',
                      'django-cors-headers==1.1.0',
                      'django-extensions==1.6.1',
                      'django-filter==0.9.2',
                      'djangorestframework==3.2.3',
                      'djangular==0.2.7',
                      'flake8==2.5.1',
                      'gunicorn==19.3.0',
                      'iso8601==0.1.11',
                      'keystoneauth1==2.1.0',
                      'lazy-object-proxy==1.2.1',
                      'mccabe==0.3.1',
                      'monotonic==0.5',
                      'msgpack-python==0.4.6',
                      'netaddr==0.7.18',
                      'netifaces==0.10.4',
                      'numpy==1.9.2',
                      'oslo.config==3.2.0',
                      'oslo.i18n==3.1.0',
                      'oslo.serialization==2.2.0',
                      'oslo.utils==3.3.0',
                      'pbr==1.8.1',
                      'pep8==1.6.2',
                      'pluggy==0.3.1',
                      'prettytable==0.7.2',
                      'py==1.4.31',
                      'pyflakes==1.0.0',
                      'pylint==1.5.4',
                      'pyparsing==2.0.3',
                      'python-dateutil==2.4.2',
                      'python-keystoneclient==2.0.0',
                      'pytz==2014.10',
                      'requests==2.9.1',
                      'rest-condition==1.0.1',
                      'six==1.9.0',
                      'sqlparse==0.1.18',
                      'stevedore==1.10.0',
                      'tox==2.3.1',
                      'virtualenv==15.0.1',
                      'wrapt==1.10.6'
                      ],
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
