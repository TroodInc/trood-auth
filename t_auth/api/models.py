# encoding: utf-8
"""
Auth Service Backend

Authentication models
"""

import datetime
import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.deprecation import CallableTrue
from django.utils.translation import ugettext_lazy as _

from .constants import OBJECT_STATUS


class AccountRole(models.Model):
    """
    One role in our system
    Role acts as a scope for permissions
    """
    name = models.CharField(max_length=128, null=False)
    status = models.SmallIntegerField(choices=OBJECT_STATUS.CHOICES)


class Account(models.Model):
    """
    One account in our system
    """

    USER = 'user'
    SERVICE = 'service'

    ACCOUNT_TYPES = (
        (USER, _('User')),
        (SERVICE, _('Service'))
    )

    login = models.CharField(max_length=64, null=False, unique=True)
    pwd_hash = models.CharField(max_length=128, null=False)

    unique_token = models.CharField(max_length=128, null=False)
    current_session = models.CharField(max_length=128, null=False)

    role = models.ForeignKey(AccountRole, null=True)

    created = models.DateTimeField(auto_now=True)
    status = models.SmallIntegerField(choices=OBJECT_STATUS.CHOICES)

    type = models.CharField(max_length=12, choices=ACCOUNT_TYPES, default=USER)
    cidr = models.CharField(max_length=20, default="0.0.0.0/0")

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
