# encoding: utf-8
"""
Auth Service Backend

Views for administration and registration/authentication processes
"""
from .admin import ActionViewSet, AccountViewSet
from t_auth.api.views.front import PermissionViewSet
from .front import (
    LoginViewSet, TwoFactorViewSet, RegistrationViewSet, CheckTokenViewSet
)
