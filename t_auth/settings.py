import os
from configurations import Configuration, values
import dj_database_url


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BaseConfiguration(Configuration):
    # Django environ
    # DOTENV = os.path.join(BASE_DIR, '.env')

    DEBUG = values.BooleanValue(True, environ_prefix='')
    # SECURITY WARNING: keep the secret key used in production secret!
    # Must be set from enviroment
    # SECRET_KEY = values.SecretValue('=y3scd+v+70xtpter(4#2^%fp3f6n^lt_*&gi9cnq0j)p7o@67')
    SECRET_KEY = values.Value('=y3scd+v+70xtpter(4#2^%fp3f6n^lt_*&gi9cnq0j)p7o@67', environ_prefix='')
    RECOVERY_LINK = values.URLValue('http://127.0.0.1/recovery?token={}', environ_prefix='')
    FROM_EMAIL = values.EmailValue('robot@trood.ru', environ_prefix='')
    EMAIL_HOST = values.Value('trood.ru', environ_prefix='')
    # Must be set from enviroment
    # EMAIL_HOST_PASSWORD = values.SecretValue('password')
    EMAIL_HOST_PASSWORD = values.Value('password', environ_prefix='')
    EMAIL_HOST_USER = values.Value('robot', environ_prefix='')
    EMAIL_PORT = values.IntegerValue(25, environ_prefix='')
    EMAIL_USE_TLS = values.BooleanValue(True, environ_prefix='')
    USER_PROFILE_DATA_URL = values.URLValue(None, environ_prefix='')
    DATABASES = {
        'default': dj_database_url.config(default='postgres://authorization:authorization@authorization_postgres/authorization')
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

        'rest_framework',
        'django_filters',

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
            'DIRS': [],
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
    # https://docs.djangoproject.com/en/1.11/topics/i18n/

    LANGUAGE_CODE = 'en-us'

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.11/howto/static-files/

    STATIC_URL = '/static/'

    # CROSS-ORIGIN STUFF
    # CORS_ORIGIN_ALLOW_ALL = True

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            't_auth.core.authentication.TroodTokenAuthentication',
        ),
        'DEFAULT_RENDERER_CLASSES': (
            't_auth.api.renderers.AuthJsonRenderer',
        ),
        'DEFAULT_FILTER_BACKENDS': (
            'django_filters.rest_framework.DjangoFilterBackend',
        ),
        'EXCEPTION_HANDLER': 't_auth.api.exception_handler.custom_exception_handler'
    }
    SERVICE_DOMAIN = values.Value("AUTHORIZATION", environ_prefix='')
    SERVICE_AUTH_SECRET = values.Value('', environ_prefix='')

    SERVICE_DOMAIN = os.environ.get("SERVICE_DOMAIN", "AUTHORIZATION")
    SERVICE_AUTH_SECRET = os.environ.get("SERVICE_AUTH_SECRET")


try:
    from custom_configuration import CustomConfiguration
except ImportError:
    class CustomConfiguration:
        pass


class Development(BaseConfiguration):
    DEBUG = True


class Production(CustomConfiguration, BaseConfiguration):
    DEBUG = False
