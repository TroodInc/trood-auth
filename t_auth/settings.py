import os
import time
from configurations import Configuration
import dj_database_url


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rel(*x):
    return os.path.normpath(os.path.join(BASE_DIR, * x))


class BaseConfiguration(Configuration):
    START_TIME = time.time()

    # Django environ
    # DOTENV = os.path.join(BASE_DIR, '.env')

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = '=y3scd+v+70xtpter(4#2^%fp3f6n^lt_*&gi9cnq0j)p7o@67'
    RECOVERY_LINK = os.environ.get('RECOVERY_LINK', "http://127.0.0.1/recovery?token={}")

    MAILER_TYPE = os.environ.get('MAILER_TYPE')

    PROJECT_NAME = os.environ.get('PROJECT_NAME')
    PROJECT_LINK = os.environ.get('PROJECT_LINK')

    if MAILER_TYPE == 'SMTP':
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

        FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL')
        EMAIL_HOST = os.environ.get('SMTP_EMAIL_HOST')
        EMAIL_HOST_PASSWORD = os.environ.get('SMTP_EMAIL_HOST_PASSWORD')
        EMAIL_HOST_USER = os.environ.get('SMTP_EMAIL_HOST_USER')
        EMAIL_PORT = os.environ.get('SMTP_EMAIL_PORT')
        EMAIL_USE_TLS = os.environ.get('SMTP_EMAIL_USE_TLS') == 'True'

    if MAILER_TYPE == 'TROOD':
        EMAIL_BACKEND = 'trood.contrib.django.mail.backends.TroodEmailBackend'

        MAIL_SERVICE_URL = os.environ.get('TROOD_MAIL_SERVICE_URL', None)

    PROFILE_STORAGE = os.environ.get('PROFILE_STORAGE', 'BUILTIN')

    if PROFILE_STORAGE == 'CUSTODIAN':
        CUSTODIAN_PROFILE_OBJECT = os.environ.get('CUSTODIAN_PROFILE_OBJECT', None)
        CUSTODIAN_PROFILE_DEPTH = os.environ.get('CUSTODIAN_PROFILE_DEPTH', 1)
        CUSTODIAN_LINK = os.environ.get('CUSTODIAN_LINK', None)

    DATABASES = {
        'default': dj_database_url.config(
            default='pgsql://authorization:authorization@authorization_postgres/authorization')
    }

    CACHE_TYPE = os.environ.get('CACHE_TYPE', None)
    CACHE_TTL = os.environ.get('CACHE_TTL', 3600)

    if CACHE_TYPE == 'REDIS':
        REDIS_URL = os.environ.get('REDIS_URL', None)

        if REDIS_URL:
            CACHES = {
                "default": {
                    "BACKEND": "django_redis.cache.RedisCache",
                    "LOCATION": REDIS_URL,
                    "OPTIONS": {
                        "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    }
                }
            }

    ALLOWED_HOSTS = ['*', ]
    # Application definition

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'corsheaders',
        'raven.contrib.django.raven_compat',

        'social_django',
        'rest_framework_social_oauth2',
        'oauth2_provider',

        'rest_framework',
        'django_filters',
        'languages',

        't_auth.api',
        't_auth.core'
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'corsheaders.middleware.CorsMiddleware',
    ]

    ROOT_URLCONF = 't_auth.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['t_auth/templates'],
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

    WSGI_APPLICATION = 't_auth.wsgi.application'

    # Password validation
    # https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

    AUTH_PASSWORD_VALIDATORS = [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    ]

    # Internationalization
    # https://docs.djangoproject.com/en/1.11/topics/i18n/

    LANGUAGE_CODE = 'en-us'

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.11/howto/static-files/

    STATIC_URL = '/static/'
    STATIC_ROOT = os.environ.get('FILE_SERVICE_STATIC_ROOT', rel('static'))

    # CROSS-ORIGIN STUFF
    # CORS_ORIGIN_ALLOW_ALL = True

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_social_oauth2.authentication.SocialAuthentication',
            't_auth.core.authentication.TroodTokenAuthentication',
        ),
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
        ),
        'DEFAULT_RENDERER_CLASSES': (
            't_auth.api.renderers.AuthJsonRenderer',
        ),
        'DEFAULT_FILTER_BACKENDS': (
            'trood.contrib.django.filters.TroodRQLFilterBackend',
            'django_filters.rest_framework.DjangoFilterBackend',
            'trood.contrib.django.auth.filter.TroodABACFilterBackend',
        ),
        'DEFAULT_PAGINATION_CLASS': 'trood.contrib.django.pagination.TroodRQLPagination',
        'EXCEPTION_HANDLER': 't_auth.api.exception_handler.custom_exception_handler'
    }

    AUTHENTICATION_BACKENDS = (
        't_auth.core.authentication.TroodOauth2Authentication',
    )

    SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['next']

    AUTH_USER_MODEL = 'api.Account'

    SERVICE_DOMAIN = os.environ.get("SERVICE_DOMAIN", "AUTHORIZATION")
    SERVICE_AUTH_SECRET = os.environ.get("SERVICE_AUTH_SECRET")

    ABAC_DEFAULT_RESOLUTION = os.environ.get("ABAC_DEFAULT_RESOLUTION", "allow")

    TROOD_OAUTH_URL = os.environ.get('TROOD_OAUTH_URL')

    REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = (
        'trood.contrib.django.auth.permissions.TroodABACPermission',
    )

    ENABLE_RAVEN = os.environ.get('ENABLE_RAVEN', "False")

    if ENABLE_RAVEN == "True":
        RAVEN_CONFIG = {
            'dsn': os.environ.get('RAVEN_CONFIG_DSN'),
            'release': os.environ.get('RAVEN_CONFIG_RELEASE')
        }

try:
    from custom_configuration import CustomConfiguration
except ImportError:
    class CustomConfiguration:
        pass


class Development(BaseConfiguration):
    DEBUG = True


class Production(CustomConfiguration, BaseConfiguration):
    DEBUG = False
