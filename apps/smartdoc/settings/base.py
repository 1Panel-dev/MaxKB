import datetime
import mimetypes
import os
from pathlib import Path

from PIL import Image

from ..const import CONFIG, PROJECT_DIR

mimetypes.add_type("text/css", ".css", True)
mimetypes.add_type("text/javascript", ".js", True)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
Image.MAX_IMAGE_PIXELS = 20000000000
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-g1u*$)1ddn20_3orw^f+g4(i(2dacj^awe*2vh-$icgqwfnbq('
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = CONFIG.get_debug()

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': CONFIG.get_db_setting()
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'users.apps.UsersConfig',
    'setting',
    'dataset',
    'application',
    'embedding',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    "drf_yasg",  # swagger 接口
    'django_filters',  # 条件过滤
    'django_apscheduler',
    'common',
    'function_lib',
    'django_celery_beat'

]

MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'common.middleware.gzip.GZipMiddleware',
    'common.middleware.static_headers_middleware.StaticHeadersMiddleware',
    'common.middleware.cross_domain_middleware.CrossDomainMiddleware',
    'common.middleware.doc_headers_middleware.DocHeadersMiddleware'
]

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=60 * 60 * 2)  # <-- 设置token有效时间
}

APPS_DIR = os.path.join(PROJECT_DIR, 'apps')
ROOT_URLCONF = 'smartdoc.urls'
# FORCE_SCRIPT_NAME
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['apps/static/ui'],
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

SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'common.config.swagger_conf.CustomSwaggerAutoSchema',
    'DEFAULT_GENERATOR_CLASS': 'common.config.swagger_conf.CustomOpenAPISchemaGenerator',
    "DEFAULT_MODEL_RENDERING": "example",
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'AUTHORIZATION',
            'in': 'header',
        }
    }
}

#  缓存配置
CACHES = {
    "default": {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 60 * 30,
        'OPTIONS': {
            'MAX_ENTRIES': 150,
            'CULL_FREQUENCY': 5,
        }
    },
    'default_file': {
        'BACKEND': 'common.cache.file_cache.FileCache',
        'LOCATION': os.path.join(PROJECT_DIR, 'data', 'cache', "default_file_cache")  # 文件夹路径
    },
    'chat_cache': {
        'BACKEND': 'common.cache.file_cache.FileCache',
        'LOCATION': os.path.join(PROJECT_DIR, 'data', 'cache', "chat_cache")  # 文件夹路径
    },
    # 存储用户信息
    'user_cache': {
        'BACKEND': 'common.cache.file_cache.FileCache',
        'LOCATION': os.path.join(PROJECT_DIR, 'data', 'cache', "user_cache")  # 文件夹路径
    },
    # 存储用户Token
    "token_cache": {
        'BACKEND': 'common.cache.file_cache.FileCache',
        'LOCATION': os.path.join(PROJECT_DIR, 'data', 'cache', "token_cache")  # 文件夹路径
    }
}

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'common.handle.handle_exception.handle_exception',
    'DEFAULT_AUTHENTICATION_CLASSES': ['common.auth.authenticate.AnonymousAuthentication']

}
STATICFILES_DIRS = [(os.path.join(PROJECT_DIR, 'ui', 'dist'))]

STATIC_ROOT = os.path.join(BASE_DIR.parent, 'static')

WSGI_APPLICATION = 'smartdoc.wsgi.application'

# 邮件配置
EMAIL_ADDRESS = CONFIG.get('EMAIL_ADDRESS')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = CONFIG.get('EMAIL_USE_TLS')  # 是否使用TLS安全传输协议(用于在两个通信应用程序之间提供保密性和数据完整性。)
EMAIL_USE_SSL = CONFIG.get('EMAIL_USE_SSL')  # 是否使用SSL加密，qq企业邮箱要求使用
EMAIL_HOST = CONFIG.get('EMAIL_HOST')  # 发送邮件的邮箱 的 SMTP服务器，这里用了163邮箱
EMAIL_PORT = CONFIG.get('EMAIL_PORT')  # 发件箱的SMTP服务器端口
EMAIL_HOST_USER = CONFIG.get('EMAIL_HOST_USER')  # 发送邮件的邮箱地址
EMAIL_HOST_PASSWORD = CONFIG.get('EMAIL_HOST_PASSWORD')  # 发送邮件的邮箱密码(这里使用的是授权码)

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


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

TIME_ZONE = CONFIG.get_time_zone()

# 启用国际化
USE_I18N = True

# 启用本地化
USE_L10N = True

# 启用时区
USE_TZ = True

# 默认语言
LANGUAGE_CODE = CONFIG.get("LANGUAGE_CODE")

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
