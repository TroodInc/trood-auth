# encoding: utf-8
"""
Auth Service Backend

Views for administration and registration/authentication processes
"""
from .admin import AccountViewSet
from .front import (
    RegistrationViewSet,
)
