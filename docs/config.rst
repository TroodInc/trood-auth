Environment variables
=====================

General settings
----------------

.. envvar:: BASE_URL


.. envvar:: SERVICE_DOMAIN

    Service identification used in TroodCore ecosystem, default `AUTHORIZATION`


.. envvar:: SERVICE_AUTH_SECRET

    Random generated string for system token authentication purposes, `please keep in secret`
    

User profile settings
---------------------

.. envvar:: RECOVERY_LINK

    Link to be sent for users initiated password recovery process
    

.. envvar:: PROFILE_STORAGE

    Where user profile must be stored, can be set tot `CUSTODIAN` or `BUILTIN`
    

.. envvar:: CUSTODIAN_PROFILE_OBJECT

    The `name` of Custodian object used for storing user profiles
    

.. envvar:: CUSTODIAN_LINK

    Url for Custodian endpoints base.
    

Notification setting
--------------------

.. envvar:: FROM_EMAIL
    

.. envvar:: EMAIL_HOST
    

.. envvar:: EMAIL_HOST_PASSWORD
    

.. envvar:: EMAIL_HOST_USER
    

.. envvar:: EMAIL_PORT
    

.. envvar:: EMAIL_USE_TLS
    


Debug settings
--------------

.. envvar:: DJANGO_CONFIGURATION

    | Service mode, cab be `Production` or `Development`.
    | `Development` mode has additional features enabled:
    | - Swagger endpoint at  `/swagger/`
    

.. envvar:: ENABLE_RAVEN

    Boolean flag for `Sentry` logging enabled `False` by default
    

.. envvar:: RAVEN_CONFIG_DSN

    Sentry project DSN URL to log events to
    

.. envvar:: RAVEN_CONFIG_RELEASE

    String tag for identify events sent into `Sentry` log
    