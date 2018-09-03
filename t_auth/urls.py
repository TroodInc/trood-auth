# encoding: utf-8
from django.conf import settings
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

import t_auth.api.views.front
import t_auth.api.views.system
from t_auth.api import views as api_views
from t_auth.api.views.admin import AccountRoleViewSet, ABACResourceViewSet, ABACActionViewSet, ABACAttributViewSet, \
    ABACPolicyViewSet

router = routers.DefaultRouter()

router.register(r'register', api_views.RegistrationViewSet, base_name='register')
router.register(r'account', api_views.AccountViewSet, base_name='account')

router.register(r'roles', AccountRoleViewSet, base_name='roles')
router.register(r'resources', ABACResourceViewSet, base_name='resources')
router.register(r'actions', ABACActionViewSet, base_name='actions')
router.register(r'attributes', ABACAttributViewSet, base_name='attributes')
router.register(r'policies', ABACPolicyViewSet, base_name='policies')

# not actually used
router.register(r'check_2fa', api_views.TwoFactorViewSet, base_name='api_2fa')

from t_auth.two_factor_auth.urls import urlpatterns as two_factor_urls

urlpatterns = [
    url(r'^api/v1.0/abac-provision', api_views.system.ABACProvisionAttributeMap.as_view(), name='provision'),
    url(r'^api/v1.0/login', api_views.front.LoginView.as_view(), name='login'),
    url(r'^api/v1.0/logout', api_views.front.LogoutView.as_view(), name='logout'),
    url(r'^api/v1.0/verify-token', t_auth.api.views.system.VerifyTokenView.as_view(), name='verify-token'),
    url(r'^api/v1.0/password-recovery', t_auth.api.views.front.RecoveryView.as_view(), name='password-recovery'),
    url(r'^api/v1.0/invalidate-token', t_auth.api.views.system.InvalidateTokenView.as_view(), name='invalidate-token'),
    url(r'^api/v1.0/', include(router.urls, namespace='api')),
    url(r'^api/v1.0/2fa/', include(two_factor_urls, namespace='2fa-auth')),

]
if settings.DEBUG:
    urlpatterns.append(url(r'^docs/', include_docs_urls(title='Trood Auth')))