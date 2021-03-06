"""
Django settings for dafoadmin_site project.

Generated by 'django-admin startproject' using Django 1.10.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
SITE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SITE_DIR)
PROJECT_DIR = os.path.dirname(BASE_DIR)


# Documentation paths
DOC_STATIC_URL = '/doc/static/'
DOC_DIR = os.path.join(PROJECT_DIR, "doc")
DOC_STATIC_DIR = os.path.join(DOC_DIR, 'static')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&k(5=@-3amupyw_67k)6rp-sj1p^x=lg)@i*_81w9jkrc_=i15'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_markup',
    'fancy_cronfield',
    'common',
    'dafousers',
    'dafoconfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dafoadmin_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dafoadmin_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'configuration': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'datafordeler',
        'USER': 'test',
        'PASSWORD': 'test',
        'HOST': '127.0.0.1',
    }
}

DATABASE_ROUTERS = ['dafoadmin_site.routers.ModelDatabaseRouter']



# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

PW_NAMESPACE = 'django.contrib.auth.password_validation'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': PW_NAMESPACE + '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': PW_NAMESPACE + '.MinimumLengthValidator',
    },
    {
        'NAME': PW_NAMESPACE + '.CommonPasswordValidator',
    },
    {
        'NAME': PW_NAMESPACE + '.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'da'

LANGUAGES = [
  ('da', _('Danish')),
]

TIME_ZONE = 'Europe/Copenhagen'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static_files")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]
MEDIA_ROOT = os.path.join(STATIC_ROOT, "media")
CERT_ROOT = os.path.join(BASE_DIR, "cert")
CERT_TMP_ROOT = os.path.join(CERT_ROOT, "tmp")

# Defaults for restructuredtext rendering in templates

MARKUP_SETTINGS = {
   'restructuredtext': {
      'settings_overrides': {
         'raw_enabled': True,
         'file_insertion_enabled': True,
      }
   }
}

# Enable or disable Django admin
ENABLE_DJANGO_ADMIN = False

# Enable session expiration on browser close
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# The name of the certificate key we sign certificates with
ROOT_CERT_NAME = "default.jks"
ROOT_CERT_PASS = 'password'
ROOT_CERT_ALIAS = 'selfsigned'

# FCGI defaults
FCGI_LOG_PATH = os.path.join(PROJECT_DIR, "logs")

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/frontpage/'
LOGOUT_REDIRECT_URL = '/'

# The URL we use for logging in via the IdP
IDP_SSOPROXY_URL = "https://localhost:7443/sso_proxy"

# How many seconds time skew to allow when checking SAML tokens
MAX_SAML_TIME_SKEW = 3

# How many seconds to allow a token to live before we reject it
MAX_SAML_TOKEN_LIFETIME = 60 * 10

# SAML audience URI, must be the same as is added to tokens by the STS
SAML_AUDIENCE_URI = "https://data.gl/"

# The issuer NameID used by the DAFA STS that issues the tokens
SAML_STS_ISSUER = "Dafo-STS"

# The public x509 cert the STS uses to sign tokens
SAML_STS_PUBLIC_CERT = """\
MIIC+zCCAeOgAwIBAgIJAKMfFL7HCxFZMA0GCSqGSIb3DQEBCwUAMBQxEjAQBgNVBAMMCWxvY2Fs
aG9zdDAeFw0xNzA0MjUwOTQzNTdaFw0yNzA0MjMwOTQzNTdaMBQxEjAQBgNVBAMMCWxvY2FsaG9z
dDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAOQ2ayxfLX0bWEhElW83nWslKBjLYY8x
0v1+rv9htGsroWclvu9srD7R5qA979bH0xX3fI0SZLAgym7YOLbEGMWjWZH5W34tKUBw2hBuEadJ
AOwU4HGaDFws/fTullYzDDiQU3NSlnIrwhSmWJYjgU39NkGu0qoBkp7x7raid0hwqOk40O5VRS2s
7q6XX+IbzTh5Fyod0JtSr8iabuLGt2xWdbNY8jlo7BkMiweygn3/1sPdzUQmY3ryoTnL5j4W0KoJ
Iqqu4UHRR7EW9R2ytySrbtBh55VcoILCbByP+4B+o896uTR+z/eZgFLDIeW3LaypGLskw731OJ/7
01dMlNkCAwEAAaNQME4wHQYDVR0OBBYEFOWkzPajQZFDeRRFkNnRY9y00lRaMB8GA1UdIwQYMBaA
FOWkzPajQZFDeRRFkNnRY9y00lRaMAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAKcm
YscBZhYjEtWzc5sdWGdvI8gJygYhFSZJu+z+T9Rw6Se4LBfJAP4iuaYrDOmB/tRsH4AlvwE5J3SR
+k/2pZ4RNLLopHzg+HlDPnkwXJqk0+ryhODriua7sEkSg6BCEohEJZvj4OHuaExYgzz7RSG34L9n
5L6tf7lvyMEXKGtvhtyMaM4lHCP5zzscv1I5q5Pa7lsxQ1V8xVMaZzyEDxf1XFXlj+a3FARX/khv
6fNAqwfHitdV7fWUoNTzFauRngfSVX7VHxlkmZlPV3rtHLRefNUBTRlincP129nJoFNynK+swr0V
6bEVjlwiNbMb7qSTYu/3oC9OIqUbgCT7t6M="""

USERPROFILE_DEBUG_TRANSLATION_MAP = {}

AUTHENTICATION_BACKENDS = [
    'dafousers.auth.DafoUsersAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOCAL_SETTINGS_FILE = os.path.join(SITE_DIR, "local_settings.py")
if os.path.exists(LOCAL_SETTINGS_FILE):
    from .local_settings import *  # noqa

# Use same database as the default for configuration, if a specific database
# has not been configured locally.
if 'configuration' not in DATABASES:
    DATABASES['configuration'] = DATABASES['default']

# The certificate key we sign certificates with
ROOT_CERT = os.path.join(CERT_ROOT, ROOT_CERT_NAME)

SELENIUM_DISPLAY = ":0"

PULLCOMMAND_HOST = 'http://localhost:8445'

# psycopg2cffi is a replacement for psycopg2 that supports PyPy
try:
    from psycopg2cffi import compat
    compat.register()
except ImportError:
    pass
