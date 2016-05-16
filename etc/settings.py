__author__ = 'simonyu, rafi Feroze'

# override the database settings

# Use `django-admin generate_secret_key` to set a secret key
# SECRET_KEY = ''

DEBUG = True

ALLOWED_HOSTS = [
    'https://crams.example.org'

]

# Set DB settings (if not set will use sqlite)
# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#        'NAME': 'crams',                      # Or path to database file if using sqlite3.
#        'USER': 'crams',
#        'PASSWORD': '',
#        'HOST': '',       # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
#        'PORT': '',                # Set to empty string for default.
#    }
# }

STATIC_ROOT = '/usr/share/crams/static/'

# Email notification configuration
EMAIL_SENDER = 'admin@example.org'

# Send email to the console by default
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Or have an smtp backend, it will send email to admin user
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# django-mailer uses a different settings attribute
MAILER_EMAIL_BACKEND = EMAIL_BACKEND

KS_USERNAME = ''
KS_PASSWORD = ''
KS_PROJECT = ''
KS_URL = ''
