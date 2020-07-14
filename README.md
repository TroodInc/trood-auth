Quickstart
----------

Download and start TroodAuthorization service container:

```bash
    docker pull registry.tools.trood.ru/auth:dev
    docker run -d -p 127.0.0.1:8000:8000/tcp \
        --env DJANGO_CONFIGURATION=Development \
        --env DATABASE_URL=sqlite://./db.sqlite3 \
        --name=authorization registry.tools.trood.ru/auth:dev
```

Initiate database structure for created container:

```bash
    docker exec authorization python manage.py migrate
```

Register your first User:

```bash
    curl -X POST 'http://127.0.0.1:8000/api/v1.0/register/' \
        -H 'Content-Type: application/json' \
        -d '{"login": "admin@demo.com", "password": "password"}'
```

Check other API methods on documentation:

```bash
    open http://127.0.0.1:8000/swagger/
```

Environment variables
=====================

General settings
----------------

BASE_URL


SERVICE_DOMAIN

    Service identification used in TroodCore ecosystem, default ``AUTHORIZATION``


SERVICE_AUTH_SECRET

    Random generated string for system token authentication purposes, ``please keep in secret``


User profile settings
---------------------

RECOVERY_LINK

    Link to be sent for users initiated password recovery process


PROFILE_STORAGE

    Where user profile must be stored, can be set to ``CUSTODIAN`` or ``BUILTIN``


CUSTODIAN_PROFILE_OBJECT

    The ``name`` of Custodian object used for storing user profiles


CUSTODIAN_LINK

    Url for Custodian endpoints base.

Cache settings
--------------

CACHE_TYPE

    Type of cache used, can be ``REDIS`` or ``NONE``


CACHE_TTL

    Cache expiration time in seconds, ``3600`` by default


REDIS_URL

    Redis server used for cache


Notification setting
--------------------

MAILER_TYPE

    Kind of email backend used to send a mails with. Can be set to ``SMTP`` or ``TROOD``


SMTP_FROM_EMAIL


SMTP_EMAIL_HOST


SMTP_EMAIL_HOST_PASSWORD


SMTP_EMAIL_HOST_USER


SMTP_EMAIL_PORT


SMTP_EMAIL_USE_TLS


TROOD_MAIL_SERVICE_URL

    TroodMail service URL, used while ``MAILER_TYPE`` set to ``TROOD`` value


Debug settings
--------------

DJANGO_CONFIGURATION

    Service mode, cab be ``Production`` or ``Development``.
    ``Development`` mode has additional features enabled:
    - Swagger endpoint at  ``/swagger/``


ENABLE_RAVEN

    Boolean flag for ``Sentry`` logging enabled ``False`` by default


RAVEN_CONFIG_DSN

    Sentry project DSN URL to log events to


RAVEN_CONFIG_RELEASE

    String tag for identify events sent into ``Sentry`` log
