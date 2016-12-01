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


# Installed the Django tests runnere
# INSTALLED_APPS += ('django_nose','django_jenkins',)

#  Indicate Django to use the Nose tests runner.
# TEST_RUNNER = 'django.tests.runner.DiscoverRunner'

# NOSE settings
# NOSE_ARGS = [
#    '--with-coverage',  # activate coverage report
#    '--with-doctest',  # activate doctest: find and run docstests
#    '--verbosity=2',  # verbose output
#    '--with-xunit',  # enable XUnit plugin
#    '--xunit-file=tests/reporter/xunittest.xml',  # the XUnit report file
#    '--cover-xml',  # produle XML coverage info
#    '--cover-xml-file=tests/reporter/coverage.xml',  # the coverage info file
#    '--cover-package=crams_api, crams',  # packages to be covered
# ]

# Jenkins Test related

# INSTALLED_APPS += ('django_jenkins',)
# JENKINS_TASKS = (
#    'django_jenkins.tasks.run_pylint',
#    'django_jenkins.tasks.with_coverage',
# )
# PROJECT_APPS = ['crams_api']
