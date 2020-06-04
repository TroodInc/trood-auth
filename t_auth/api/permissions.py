# encoding: utf-8
from rest_framework import permissions


class PublicEndpoint(permissions.BasePermission):
    """
    Helper to check the permission.
    """
    def has_permission(self, request, view):
        return True
