import os

# Избавиться
# Нет необходимости в "размазывании" настроек
# Достаточно env файла
from configurations import Configuration

import environ


class BaseConfiguration(Configuration):
    # Django environ
    root = environ.Path(__file__) - 1
    env = environ.Env(
        DEBUG=(bool, True),
        SECRET_KEY=(str, '=y3scd+v+70xtpter(4#2^%fp3f6n^lt_*&gi9cnq0j)p7o@67'),
        RECOVERY_LINK = (str, 'http://127.0.0.1/recovery?token={}'),
        FROM_EMAIL=(str, 'robot@trood.ru'),
        EMAIL_HOST=(str, 'trood.ru'),
        EMAIL_HOST_PASSWORD=(str, 'password'),
        EMAIL_HOST_USER=(str, 'robot'),
        EMAIL_PORT=(int, 25),
        EMAIL_USE_TLS=(bool, True),
        USER_PROFILE_DATA_URL=(str, ''),
    )

    environ.Env.read_env(env_file=root('.env'))

    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    DEBUG=env('DEBUG')

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = env('SECRET_KEY')

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

    RECOVERY_LINK = env('RECOVERY_LINK')
    FROM_EMAIL = env('FROM_EMAIL')

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    EMAIL_HOST = env('EMAIL_HOST')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_PORT = env('EMAIL_PORT')
    EMAIL_USE_TLS = env('EMAIL_USE_TLS')

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

    DATABASES = {
        'default': env.db(
            default='postgres://authorization:authorization@authorization_postgres/authorization'
        )
    }

    USER_PROFILE_DATA_URL = env('USER_PROFILE_DATA_URL')


try:
    from custom_configuration import CustomConfiguration
except ImportError:
    class CustomConfiguration:
        pass


class Development(BaseConfiguration):
    DEBUG = True


class Production(CustomConfiguration, BaseConfiguration):
    DEBUG = False
