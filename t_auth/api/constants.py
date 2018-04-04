# encoding: utf-8
"""
Auth Service Backend

Constants
"""


class OBJECT_PERMISSION:
    OWN_OBJECTS = 1
    CHILD_OBJECTS = 2
    ALL_OBJECTS = 128

    CHOICES = (
        (OWN_OBJECTS, 'own_objects'),
        (CHILD_OBJECTS, 'child_objects'),
        (ALL_OBJECTS, 'all_objects')
    )


class OBJECT_STATUS:
    ACTIVE = 1
    DISABLED = 2
    DELETED = 128

    CHOICES = (
        (ACTIVE, 'active'),
        (DISABLED, 'disabled'),
        (DELETED, 'deleted')
    )
