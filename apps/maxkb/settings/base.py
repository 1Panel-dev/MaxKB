"""
Django settings for maxkb project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from ..const import CONFIG, PROJECT_DIR
import os
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-zm^1_^i5)3gp^&0io6zg72&z!a*d=9kf9o2%uft+27l)+t(#3e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = CONFIG.get_debug()

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'users.apps.UsersConfig',
    'tools.apps.ToolConfig',
    'knowledge',
    'common',
    'system_manage',
    'models_provider',
    'django_celery_beat',
    'application',
    'chat',
    'oss',
    'django_apscheduler',
]

MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'common.middleware.gzip.GZipMiddleware',
    'common.middleware.chat_headers_middleware.ChatHeadersMiddleware',
    'common.middleware.cross_domain_middleware.CrossDomainMiddleware',
    'common.middleware.doc_headers_middleware.DocHeadersMiddleware',

]

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'common.exception.handle_exception.handle_exception',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': ['common.auth.authenticate.AnonymousAuthentication']
}
STATICFILES_DIRS = [(os.path.join(PROJECT_DIR, 'ui', 'dist'))]
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'static')
ROOT_URLCONF = 'maxkb.urls'
APPS_DIR = os.path.join(PROJECT_DIR, 'apps')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["apps/static/admin"],
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
    {"NAME": "CHAT",
     'BACKEND': 'django.template.backends.django.DjangoTemplates',
     'DIRS': ["apps/static/chat"],
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
    {"NAME": "DOC",
     'BACKEND': 'django.template.backends.django.DjangoTemplates',
     'DIRS': ["apps/static/drf_spectacular_sidecar"],
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
SPECTACULAR_SETTINGS = {
    'TITLE': 'MaxKB API',
    'DESCRIPTION': _('Intelligent customer service platform'),
    'VERSION': 'v2',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
    'SWAGGER_UI_DIST': '/doc/swagger-ui-dist',  # shorthand to use the sidecar instead
    'SWAGGER_UI_FAVICON_HREF': '/doc/swagger-ui-dist/favicon-32x32.png',
    'REDOC_DIST': '/doc/redoc',
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'AUTHORIZATION',
            'in': 'header',
        }
    }
}
WSGI_APPLICATION = 'maxkb.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {'default': CONFIG.get_db_setting()}

CACHES = CONFIG.get_cache_setting()

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = CONFIG.get("LANGUAGE_CODE")

TIME_ZONE = CONFIG.get_time_zone()

USE_I18N = True

USE_TZ = True
# 支持的语言
LANGUAGES = [
    ('en', 'English'),
    ('zh', '中文简体'),
    ('zh-hant', '中文繁体')
]
# 翻译文件路径
LOCALE_PATHS = [
    os.path.join(BASE_DIR.parent, 'locales')
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

edition = 'CE'

if os.environ.get('MAXKB_REDIS_SENTINEL_SENTINELS') is not None:
    DJANGO_REDIS_CONNECTION_FACTORY = "django_redis.pool.SentinelConnectionFactory"
