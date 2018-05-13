# encoding: utf-8
"""
Auth Service Backend

Authentication models
"""
import hashlib

import datetime
import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.deprecation import CallableTrue
from django.utils.translation import ugettext_lazy as _

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
    role = models.ForeignKey(AccountRole, null=True)

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

    @property
    def is_authenticated(self):
        return CallableTrue


class Token(models.Model):
    RECOVERY = 'recovery'
    AUTHORIZATION = 'authorization'

    TOKEN_TYPES = (
        (RECOVERY, _('Recovery')),
        (AUTHORIZATION, _('Authorization'))
    )

    token = models.CharField(max_length=64, null=False)
    account = models.ForeignKey(Account)
    expire = models.DateTimeField(null=False)
    type = models.CharField(_('Type'), max_length=24, choices=TOKEN_TYPES, default=AUTHORIZATION)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.id:
            self.expire = datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(days=1)
            self.token = uuid.uuid4().hex
            super(Token, self).save()


class ABACResource(models.Model):
    domain = models.CharField(max_length=128, null=False)
    comment = models.TextField()
    name = models.CharField(max_length=64, null=False)


class ABACAction(models.Model):
    resource = models.ForeignKey(ABACResource, null=False, related_name="actions")
    name = models.CharField(max_length=64, null=False)


class ABACAttribute(models.Model):
    resource = models.ForeignKey(ABACResource, null=False, related_name="attributes")
    name = models.CharField(max_length=64, null=False)
    attr_type = models.CharField(max_length=64, null=False)


class ABACPolicy(models.Model):
    domain = models.CharField(max_length=128, null=False)
    resource = models.ForeignKey(ABACResource, null=True)
    action = models.ForeignKey(ABACAction, null=True)


class ABACRule(models.Model):
    ALLOW = 'allow'
    DENY = 'deny'

    RESULT_TYPES = (
        (ALLOW, _('Allow')),
        (DENY, _('Deny'))
    )

    result = models.CharField(max_length=64, choices=RESULT_TYPES, null=False)
    rule = JSONField()
    policy = models.ForeignKey(ABACPolicy, null=True, related_name="rules")
