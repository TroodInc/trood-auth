# encoding: utf-8
"""
Auth Service Backend

Authentication models
"""
import hashlib

from django.db import models

from .constants import OBJECT_STATUS, OBJECT_PERMISSION


class Endpoint(models.Model):
    url = models.CharField(max_length=255, unique=True)


class AccountPermission(models.Model):
    """
    One permission object
    """
    endpoint = models.ForeignKey(Endpoint)
    method = models.CharField(max_length=32, null=False)
    object_permission = models.SmallIntegerField(choices=OBJECT_PERMISSION.CHOICES)


class AccountRole(models.Model):
    """
    One role in our system
    Role acts as a scope for permissions
    """
    name = models.CharField(max_length=128, null=False)
    permissions = models.ManyToManyField(AccountPermission)

    status = models.SmallIntegerField(choices=OBJECT_STATUS.CHOICES)


class Account(models.Model):
    """
    One account in our system
    """
    login = models.CharField(max_length=64, null=False, unique=True)
    pwd_hash = models.CharField(max_length=128, null=False)

    unique_token = models.CharField(max_length=128, null=False)
    current_session = models.CharField(max_length=128, null=False)

    permissions = models.ManyToManyField(AccountPermission)

    created = models.DateTimeField(auto_now=True)
    status = models.SmallIntegerField(choices=OBJECT_STATUS.CHOICES)

    @classmethod
    def check_session(cls, session_code):
        """
        Checks session code
        """
        sess, signed_str = session_code.split('.')

        my_user = Account.objects.get(
            status__exact=OBJECT_STATUS.ACTIVE,
            current_session__exact=sess
        )

        # check with signed session
        check_str = hashlib.sha256(
            (str(my_user.id) + sess + my_user.unique_token).encode('utf-8')
        ).hexdigest()

        if signed_str != check_str:
            return None

        return my_user

    def create_session(self):
        """
        Creates session token
        """
        if not self.id:
            raise Exception('No user data present when creating session!')

        # unique session token
        x_now = datetime.datetime.now().strftime('%d.%m.%Y.%H.%M.%S.%f')
        full_str = x_now + self.create_token()
        hashed_session = hashlib.sha256(full_str.encode('utf-8')).hexdigest()

        # signed token + current user ID
        sign_str = hashlib.sha256(
            (str(self.id) + hashed_session + self.unique_token).encode('utf-8')
        ).hexdigest()

        # combine into a single string
        full_sess_str = '.'.join((hashed_session, sign_str))

        return full_sess_str

    def has_permission(self, permission_code):
        """
        Checks if this user has permission with provided permission code
        """
        my_permissions = [x.code for x in self.permissions]
        return permission_code in my_permissions and permission_code
