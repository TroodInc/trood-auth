# encoding: utf-8
"""
Auth Service Backend

Authentication models
"""

import datetime
import uuid

from trood.api.custodian.objects import Object
from jsonfield import JSONField
from django.db import models, transaction
from django.utils import timezone
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from languages.fields import LanguageField
from rest_framework.exceptions import ValidationError
from trood.api.custodian.records.model import Record
from trood.core.utils import get_service_token
from trood.api.custodian import client

ALLOW = 'allow'
DENY = 'deny'

RESULT_TYPES = (
    (ALLOW, _('Allow')),
    (DENY, _('Deny'))
)

class AccountRole(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_DISABLED = 'disabled'
    STATUS_DELETED = 'deleted'

    ROLE_STATUS = (
        (STATUS_ACTIVE, _('Active')),
        (STATUS_DISABLED, _('Disabled')),
        (STATUS_DELETED, _('Deleted'))
    )
    """
    One role in our system
    Role acts as a scope for permissions
    """
    name = models.CharField(max_length=128, null=False)
    status = models.CharField(max_length=32, choices=ROLE_STATUS, default=STATUS_ACTIVE)


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

    STATUS_ACTIVE = 'active'
    STATUS_DISABLED = 'disabled'
    STATUS_DELETED = 'deleted'

    ACCOUNT_STATUS = (
        (STATUS_ACTIVE, _('Active')),
        (STATUS_DISABLED, _('Disabled')),
        (STATUS_DELETED, _('Deleted'))
    )

    login = models.CharField(max_length=64, null=False, unique=True)
    pwd_hash = models.CharField(max_length=128, null=False)

    unique_token = models.CharField(max_length=128, null=False)
    current_session = models.CharField(max_length=128, null=False)

    role = models.ForeignKey(AccountRole, null=True, on_delete=models.CASCADE)

    created = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=32, choices=ACCOUNT_STATUS, default=STATUS_ACTIVE)

    active = models.BooleanField(_('Active'), default=True)

    type = models.CharField(max_length=12, choices=ACCOUNT_TYPES, default=USER)
    cidr = models.CharField(max_length=20, default="0.0.0.0/0")

    profile_data = JSONField(null=True)
    profile_id = models.IntegerField(null=True)

    language = LanguageField(null=True)

    @property
    def is_authenticated(self):
        return True

    @transaction.atomic
    def delete(self, *args, **kwargs):
        if settings.PROFILE_STORAGE == "CUSTODIAN":
            try:
                custodian = client.Client(settings.CUSTODIAN_LINK, get_service_token())
                obj = custodian.objects.get(settings.CUSTODIAN_PROFILE_OBJECT)

                if self.profile_id:
                    custodian.records.delete(Record(obj, id=self.profile_id))
            except Exception as e:
                raise ValidationError({"error": e})

        super(Account, self).delete(*args, **kwargs)

    @transaction.atomic
    def save(self, *args, **kwargs):
        super(Account, self).save(*args, **kwargs)
        if settings.PROFILE_STORAGE == "CUSTODIAN":
            try:
                custodian = client.Client(settings.CUSTODIAN_LINK, get_service_token())
                obj = custodian.objects.get(settings.CUSTODIAN_PROFILE_OBJECT)

                if self.profile_id and self.profile_data:
                    custodian.records.partial_update(obj, self.profile_id, self.profile_data, depth=1)
                else:
                    profile_data = self.profile_data if self.profile_data else {}
                    record = custodian.records.create(Record(obj, id=self.pk, **profile_data))
                    self.profile_id = record.get_pk()
                    self.save()

            except Exception as e:
                raise ValidationError({"error": e})


    @property
    def profile(self):
        if settings.PROFILE_STORAGE == "CUSTODIAN":
            custodian = client.Client(settings.CUSTODIAN_LINK, get_service_token())
            obj = Object(name=settings.CUSTODIAN_PROFILE_OBJECT, cas=False, objects_manager=None)

            if self.profile_id is not None:
                record = custodian.records.get(obj, self.profile_id, depth=1)
                return record.data
            else:
                return None
        else:
            return self.profile_data

    @profile.setter
    def profile(self, value):
        self.profile_data = value


class Token(models.Model):
    RECOVERY = 'recovery'
    AUTHORIZATION = 'authorization'

    TOKEN_TYPES = (
        (RECOVERY, _('Recovery')),
        (AUTHORIZATION, _('Authorization'))
    )

    token = models.CharField(max_length=64, null=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    expire = models.DateTimeField(null=False)
    type = models.CharField(_('Type'), max_length=24, choices=TOKEN_TYPES, default=AUTHORIZATION)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.id:
            self.expire = datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(days=1)
            self.token = uuid.uuid4().hex
            super(Token, self).save()


class ABACDomain(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    default_result = models.CharField(max_length=64, choices=RESULT_TYPES, null=True)


class ABACResource(models.Model):
    domain = models.ForeignKey(ABACDomain, null=True, related_name="domain", on_delete=models.CASCADE)
    comment = models.TextField()
    name = models.CharField(max_length=64, null=False)


class ABACAction(models.Model):
    resource = models.ForeignKey(ABACResource, null=False, related_name="actions", on_delete=models.CASCADE)
    name = models.CharField(max_length=64, null=False)


class ABACAttribute(models.Model):
    resource = models.ForeignKey(ABACResource, null=False, related_name="attributes", on_delete=models.CASCADE)
    name = models.CharField(max_length=64, null=False)
    attr_type = models.CharField(max_length=64, null=False)


class ABACPolicy(models.Model):
    domain = models.CharField(max_length=128, null=False)
    resource = models.ForeignKey(ABACResource, null=True, on_delete=models.CASCADE)
    action = models.ForeignKey(ABACAction, null=True, on_delete=models.CASCADE)


class ABACRule(models.Model):
    result = models.CharField(max_length=64, choices=RESULT_TYPES, null=False)
    rule = JSONField()
    mask = models.ManyToManyField(ABACAttribute)
    policy = models.ForeignKey(ABACPolicy, null=True, related_name="rules", on_delete=models.CASCADE)
