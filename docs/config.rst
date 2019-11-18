Environment variables
=====================

General settings
----------------

.. envvar:: BASE_URL


.. envvar:: SERVICE_DOMAIN

    Service identification used in TroodCore ecosystem, default ``AUTHORIZATION``


.. envvar:: SERVICE_AUTH_SECRET

    Random generated string for system token authentication purposes, ``please keep in secret``
    

User profile settings
---------------------

.. envvar:: RECOVERY_LINK

    Link to be sent for users initiated password recovery process
    

.. envvar:: PROFILE_STORAGE

    Where user profile must be stored, can be set to ``CUSTODIAN`` or ``BUILTIN``
    

.. envvar:: CUSTODIAN_PROFILE_OBJECT

    The ``name`` of Custodian object used for storing user profiles
    

.. envvar:: CUSTODIAN_LINK

    Url for Custodian endpoints base.
    

Notification setting
--------------------

.. envvar:: MAILER_TYPE

    Kind of email backend used to send a mails with. Can be set to ``SMTP`` or ``TROOD``


.. envvar:: SMTP_FROM_EMAIL
    

.. envvar:: SMTP_EMAIL_HOST
    

.. envvar:: SMTP_EMAIL_HOST_PASSWORD
    

.. envvar:: SMTP_EMAIL_HOST_USER
    

.. envvar:: SMTP_EMAIL_PORT
    

.. envvar:: SMTP_EMAIL_USE_TLS


.. envvar:: TROOD_MAIL_SERVICE_URL

    TroodMail service URL, used while ``MAILER_TYPE`` set to ``TROOD`` value


Debug settings
--------------

.. envvar:: DJANGO_CONFIGURATION

    | Service mode, cab be ``Production`` or ``Development``.
    | ``Development`` mode has additional features enabled:
    | - Swagger endpoint at  ``/swagger/``
    

.. envvar:: ENABLE_RAVEN

    Boolean flag for ``Sentry`` logging enabled ``False`` by default
    

.. envvar:: RAVEN_CONFIG_DSN

    Sentry project DSN URL to log events to
    

.. envvar:: RAVEN_CONFIG_RELEASE

    String tag for identify events sent into ``Sentry`` log
    