Authorization service
=============



Quickstart
----------

Download and start TroodAuthorization service container:

.. code-block:: bash

    docker pull registry.tools.trood.ru/auth:dev
    docker run -d -p 127.0.0.1:8000:8000/tcp \
        --env DJANGO_CONFIGURATION=Development \
        --env DATABASE_URL=sqlite://./db.sqlite3 \
        --name=authorization registry.tools.trood.ru/auth:dev


Initiate database structure for created container:

.. code-block:: bash

    docker exec authorization python manage.py migrate


Register your first User:

.. code-block:: bash

    curl -X POST 'http://127.0.0.1:8000/api/v1.0/register/' \
        -H 'Content-Type: application/json' \
        -d '{"login": "admin@demo.com", "password": "password"}'


Check other API methods on documentation:

.. code-block:: bash

    open http://127.0.0.1:8000/swagger/



Contents
--------

.. toctree::
   :maxdepth: 2
   :glob:

   rest-api
   autoapi/index