# coding=utf-8
"""
    Test setting.py
"""
from crams.settings import *   # noqa
from crams.settings import REST_FRAMEWORK   # to avoid F405
import os  # To avoid F405


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join('tests', 'crams_test.db'),
    }
}

SECRET_KEY = 'secret'

# Set the djangorestframework testing
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication'
    )
REST_FRAMEWORK.update({
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer'
    )
})

# Allocation Home
ALLOCATION_HOME_MONASH = 'monash'
