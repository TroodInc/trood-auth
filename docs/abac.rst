
ABAC configuration
=========================================


.. contents:: The table of contents

Getting active rules
-------
Each time you authorizing user by credentials using  /api/v1.0/login/  you will receive full tree of active ABAC rules in FRONTEND domain::

  {
    "status": "OK",
    "data": {
        "id": 15,

        ...,

        "abac": {
            "employee": {
                "delete": [{
                    "active": true,
                    "result": "allow",
                    "rule": {
                        "sbj.role": "manager"
                    }
                 }, {...}]
            }
        },
  }
"**abac**" filed will be returned as a dict with resources tree structure::

  abac: {
    *: {
        *: [{rule}]
        delete: [{rule}]
    }
    resource_1: {
        *: [{rule}],
        action_1: [{rule}, {rule}],
        action_2: [{rule}]
    }
    resource_2: {
        action_1: [{rule}, {rule}]
    }
  }

.. tip::

   \* **(wildcard)**  selector can be used for resources and actions and have a lower priority then the named rules.



Configuring ABAC
-------
- ABAC can be configured using PATCH request on /api/v1.0/policies

  ``PATCH /api/v1.0/policies/8``::

    {
    "id": 8,
    "domain": "CUSTODIAN",
    "resource": 8,
    "action": 8,
    "rules": [
        {
            "result": "allow",
            "active": true,
            "rule": {
            "and": [
                 {
                       "obj.member.id": "sbj.linked_object.id"
                },
                {
                       "sbj.linked_object.role": {
                            "in": [
                                  3,
                                  4,
                                  5
                            ]
                        }
                    }
                ]
            }
        }
    ]
    }



Domain
-------
Authorization ABAC configuration should be defined in domain AUTHORIZATION


Resources
-------
Available resources are: *account*, *role*.


Actions
-------
Available actions for your resource.

.. attribute:: create

    Access for adding both *list* or *single* object.

.. attribute:: retrieve

    Access for getting *single* object.

.. attribute:: update

    Access for editing both *list* or *single* object.

.. attribute:: destroy

    Access for deleting both *list* or *single* object.

.. attribute:: list

     Access for getting both *list* or *single* object.

Attributes
-------
Now you can create policy with rules


Rules can be configured on next attributes:

Subject attributes
~~~~~~~~~~~~~~~~~~~~~
.. attribute:: sbj.id

     System-wide user ID.

.. attribute:: sbj.login

     User login string.

.. attribute:: sbj.created

     Timestamp of account creation.

.. attribute:: sbj.status

     Status of the account can be *active*, *disabled* or *deleted*. Default is *active*.

.. attribute:: sbj.active

     Active status, can be ``True`` for active or ``False`` for not active user.

.. attribute:: sbj.role

     Id of account role

.. attribute:: sbj.type

     Type of account can be either *user* or *service*. Default is *user*.

.. attribute:: sbj.cidr

     Default is ``0.0.0.0/0``.

.. attribute:: sbj.profile

     Map with additional user profile fields.

Context attributes
~~~~~~~~~~~~~~~~~~~~~

.. attribute:: ctx.data

    Map POST json body


.. attribute:: ctx.params

    List of url path chunks


.. attribute:: ctx.query

    Map of GET query params