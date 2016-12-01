# coding=utf-8
"""
Django settings for crams_app project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import logging
import os

from crams import DBConstants

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


SECRET_KEY = 'secret-development-key-override-in-local-settings'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []
# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django_extensions',
    'django_babel',
    'django_filters',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'crams.account',
    'crams',
    'crams.api',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    # CorsMiddleware needs to come before Django's CommonMiddleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'crams.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
                 os.path.join(BASE_DIR, 'crams/templates'),
                 ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG
        },
    },
]

# Custom User model
AUTH_USER_MODEL = 'account.User'

# A Django App that adds CORS (Cross-Origin Resource Sharing) headers to
# responses. CorsMiddleware needs to come before Django's CommonMiddleware
# if you are using Django's USE_ETAGS = True setting, otherwise the CORS
# headers will be lost from the 304 not-modified responses, causing errors
# in some browsers.
#
# Configuration:
# 1. set CORS_ORIGIN_ALLOW_ALL = True
# or
# 2. set CORS_ORIGIN_WHITELIST
#
# For more details see https://github.com/simonyuau/django-cors-headers

CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_CREDENTIALS = False
# CORS_REPLACE_HTTPS_REFERER = True

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.sqlite3',
        # 'vicnode',  # Or path to database file if using sqlite3.
        'NAME': 'crams.db',
        'USER': '',
        'PASSWORD': 'vn_',
        # Empty for localhost through domain sockets or '127.0.0.1' for
        # localhost through TCP.
        'HOST': '',
        'PORT': '',  # Set to empty string for default.
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'crams.rest_utils.BrowsableAPIRendererWithoutForms',
    ),
}

# Keystone Admin client
KS_USERNAME = ''
KS_PASSWORD = ''
KS_PROJECT = ''

# NeCTAR Keystone auth url
KS_URL = ""

# Crams Token Expiry Time
TOKEN_EXPIRY_TIME_SECONDS = 4 * 60 * 60

# APPROVER ROLES
NECTAR_APPROVER_ROLE = 'AllocationAdmin'
VICNODE_APPROVER_ROLE = 'vicnode_approver'

# PROJECT_ID Prefix Validation
NECTAR_PREFIX_INVALID = ['pt-']

PROJECT_SYSTEM_ID_INVALID_PREFIX_MAP = {
    DBConstants.SYSTEM_NECTAR.lower(): NECTAR_PREFIX_INVALID
}

CRAMS_UNIQUE_PROJECT_ID_LIST = [DBConstants.SYSTEM_NECTAR]

# PROVISONER ROLES
CRAMS_PROVISIONER_ROLE = 'crams_provisioner'

# CRAMS Frontend Keystone login page
CRAMS_CLIENT_COOKIE_KEY = 'client_url'
HTML_ENCODE_HASH_CHAR = '%23'
# Do not remove trailing slash
CLIENT_KS_LOGIN_PATH = '/' + HTML_ENCODE_HASH_CHAR + '/ks-login/'
NECTAR_CLIENT_BASE_URL = ''
NECTAR_CLIENT_VIEW_REQUEST_PATH = '/#/allocations/view_request/'

CRAMS_RC_SHIB_URL_PART = 'https://example.org/rcshibboleth/?return-path='

# Default Email setup to console
# Email notification configuration
EMAIL_SENDER = 'admin@crams.dev'
NECTAR_NOTIFICATION_REPLY_TO = [EMAIL_SENDER]

# Send email to the console by default
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# django-mailer uses a different settings attribute
MAILER_EMAIL_BACKEND = EMAIL_BACKEND

# Configure these for outgoing email server
# EMAIL_HOST = 'localhost'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-au'
TIME_ZONE = 'Australia/Melbourne'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Do not use STATIC PATH variable, everytime a new app is added,
# collect all static files using python manage.py collectstatic

# STATIC_PATH = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

APPEND_SLASH = True

# DEBUG_RELATED
APP_ENV = None
DEBUG_APPROVERS = []

# Import the local_settings.py to override some of the default settings,
# like database settings
try:
    from crams.local.local_settings import *   # noqa
except ImportError:
    logging.debug("No local_settings file found.")

# Used for production installs
try:
    with open("/etc/crams/settings.py") as f:
        code = compile(f.read(), "/etc/crams/settings.py", 'exec')
        exec(code)
except IOError:
    logging.debug("No settings file found at /etc/crams/settings.py.")
