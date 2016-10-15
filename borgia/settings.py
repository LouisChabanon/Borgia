"""
Django settings for borgia project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
#-*- coding: utf-8 -*-

import os, re

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'd8!^$6uved6+1d)iiqwhf5q8ao3*z)ykfdff3&zi4@i7pv#jzd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []  # 'www.borgia.iresam.org' en prod, '*' pour une simulation de prod en local.


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'shops',
    'notifications',
    'finances',
    'settings_data',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'contrib.models.LoginRequiredMiddleware',
    'contrib.models.RedirectLoginProfile',
]

ROOT_URLCONF = 'borgia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # Permet de rajouter extra à la
            'builtins': ['users.templatetags.users_extra']
        },
    },
]

WSGI_APPLICATION = 'borgia.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en²/1.9/howto/static-files/
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = '/users/profile/'
LOGIN_URL = '/auth/login'

LOGIN_EXEMPT_URLS = [
    '/auth/login',
    '/auth/password_reset/',
    '/auth/password_reset/done/',
    '/auth/done/',
    '/users/username_from_username_part',
    '/finances/electrovanne/request1',
    '/finances/electrovanne/request2',
    '/finances/electrovanne/date',
    '/foyer',
    '/auberge',
    '/finances/supply/lydia/self/callback',
    '/local/jsi18n',
    '/admin/'
]

LOGIN_EXEMPT_URL_PATTERNS = [
    re.compile('%s[0-9A-Z-a-z_\-]+%s.+%s' % ('/auth/', '/', '/')),
]

STATIC_URL = '/static/'
# STATIC_ROOT = 'static/static_root/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static', 'static_root')
STATICFILES_DIRS = (
    # 'static/static_dirs/',
    os.path.join(BASE_DIR, 'static', 'static_dirs'),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'static', 'media')
MEDIA_URL = '/media/'

# Lydia
LYDIA_API_TOKEN = '55f18739e5409079915994'
LYDIA_VENDOR_TOKEN = '55f18739e2c95650506777'
LYDIA_CALLBACK_URL = 'https://borgia.iresam.org/finances/supply/lydia/self/callback'  # https ou non selon le dns
LYDIA_CONFIRM_URL = 'http://borgia.iresam.org/finances/supply/lydia/self/confirm'

# Penser à activer 'autoriser l'acces par les applications moins sécurisées' dans Gmail
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'ae.ensam.assoc@gmail.com'
SERVER_EMAIL = 'ae.ensam.assoc@gmail.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'ae.ensam.assoc@gmail.com'
EMAIL_HOST_PASSWORD = 'Alexandre57'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Electrovanne
ELECTROVANNE_TOKEN = '80eg11TBAiR13UCI3dJKHWa5e7764KA3'

ADMINS = [('Alexandre', 'a-palo@laposte.net'), ('Guillaume', 'guillaume@broggi.ovh')]

# Durée de validité du token reset password
PASSWORD_RESET_TIMEOUT_DAYS = 1  # en jours

# Deconnection automatique
SESSION_COOKIE_AGE = 7200 

# Les paramètres modifiables sont des objets Settings de l'app settings_data
# A modifier directement dans l'application
# [LYDIA_MIN_PRICE, LYDIA_MAX_PRICE, MARGIN_PROFIT]
