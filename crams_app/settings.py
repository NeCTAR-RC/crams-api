# coding=utf-8
"""
Django settings for crams_app project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$(p5&qqx4q6z1o)@83u)dp7ez#b$!p9%*d4dccb=1$40@5xbcz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

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
    # A Django App that adds CORS (Cross-Origin Resource Sharing) headers to
    # responses.
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'crams_app',
    'crams.account',
    'crams',
    'crams.api',
    # 'ttags',
    # 'csvimport',
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

ROOT_URLCONF = 'crams_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
                 os.path.join(BASE_DIR, 'crams_app/templates'),
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

WSGI_APPLICATION = 'crams_app.wsgi.application'

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
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'vicnode',  # Or path to database file if using sqlite3.
        'NAME': 'melvin',
        'USER': 'vn_reporting',
        'PASSWORD': 'vn_reporting',
        # Empty for localhost through domain sockets or '127.0.0.1' for
        # localhost through TCP.
        'HOST': '',
        'PORT': '',  # Set to empty string for default.
    }
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    #    'DEFAULT_PERMISSION_CLASSES': [
    #        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    #        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    #    ]
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    # Other
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    # 'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    # 'ALLOWED_VERSIONS': ['v1', 'v2'],
    # 'DEFAULT_VERSION': 'v1',
    # Pagination Fields
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 2,
}

# Keystone Admin client
KS_USERNAME = ''
KS_PASSWORD = ''
KS_PROJECT = ''

# NeCTAR Keystone auth url
KEYSTONE_AUTH_URL = "https://keystone.test.rc.nectar.org.au:5000/v3/"

# CRAMS Frontend Keystone login page
CRAMS_CLIENT_COOKIE_KEY = 'client_url'
# Do not remove trailing slash
NECTAR_CLIENT_URL = 'http://118.138.245.209/#/ks-login/'
CRAMS_RC_SHIB_URL_PART = \
    'https://accounts.test.rc.nectar.org.au/rcshibboleth/?return-path='
# CRAMS_KS_LOGIN_URL = "http://118.138.245.209/app/#/ks-login/"

# Default Email setup to console
# Email notification configuration
EMAIL_SENDER = 'admin@crams.org.au'

# Send email to the console by default
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# django-mailer uses a different settings attribute
MAILER_EMAIL_BACKEND = EMAIL_BACKEND

# Configure these for outgoing email server
EMAIL_HOST = 'smtp.monash.edu'

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

APPEND_SLASH = False


# DEBUG_RELATED
APP_ENV = None
DEBUG_APPROVERS = None

# Import the local_settings.py to override some of the default settings,
# like database settings
try:
    from local.local_settings import *
except ImportError:
    logging.warning("No local_settings file found.")