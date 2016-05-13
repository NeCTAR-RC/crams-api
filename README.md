# crams-api
CRAMS API

This is a stand-alone WSGI application to manage NeCTAR resource allocation requests and implement relevant policy

This component's RESTful API is developed using django rest framework (http://www.django-rest-framework.org/)

Setting up a Dev env
====================

virtualenv -p python3.5 .venv
. .venv/bin/activate

pip install -e .

cp crams/local/local_settings.py.example crams/local/local_settings.py

Edit settings

django-admin syncdb
django-admin runserver

