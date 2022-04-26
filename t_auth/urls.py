# encoding: utf-8
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework import routers

import t_auth.api.views.front
import t_auth.api.views.system
from t_auth.api import views as api_views
from t_auth.api.views.admin import AccountRoleViewSet, ABACResourceViewSet, ABACActionViewSet, ABACAttributViewSet, \
    ABACPolicyViewSet, ABACDomainViewSet, ABACRuleViewSet

from t_auth.api.views.system import ProbeViewset, VerifyTokenViewSet, InvalidateTokenView

from trood.contrib.django.apps.fixtures.views import TroodFixturesViewSet
from trood.contrib.django.apps.meta.views import TroodMetaView

router = routers.DefaultRouter()

router.register(r'account', api_views.AccountViewSet, basename='account')

router.register(r'roles', AccountRoleViewSet, basename='roles')
router.register(r'rules', ABACRuleViewSet, basename='rules')
router.register(r'resources', ABACResourceViewSet, basename='resources')
router.register(r'actions', ABACActionViewSet, basename='actions')
router.register(r'attributes', ABACAttributViewSet, basename='attributes')
router.register(r'policies', ABACPolicyViewSet, basename='policies')
router.register(r'domains', ABACDomainViewSet, basename='domains')

router.register(r'verify-token', VerifyTokenViewSet, basename='verify-token')

router.register(r'probe', ProbeViewset, basename='probe')

if settings.DEBUG:
    router.register(r'fixtures', TroodFixturesViewSet, basename='fixtures')

urlpatterns = [
    url(r'meta', TroodMetaView.as_view(), name='meta'),
    url(r'^api/v1.0/abac', api_views.system.ABACProvisionAttributeMap.as_view(), name='abac'),
    url(r'^api/v1.0/invalidate-token', InvalidateTokenView.as_view(), name='invalidate-token'),
    url(r'^api/v1.0/login/$', api_views.front.LoginView.as_view(), name='login'),
    url(r'^api/v1.0/login/trood', api_views.system.AccessTokenRegistration.as_view(), name='token-registration'),
    url(r'^api/v1.0/login/facebook', api_views.front.FacebookAuth.as_view(), name='facebook-login'),
    url(r'^api/v1.0/gdpr/facebook', api_views.system.FacebookDataDeletion.as_view(), name='gdpr-facebook'),
    url(r'^api/v1.0/login/apple', api_views.front.AppleAuth.as_view(), name='apple-login'),
    url(r'^api/v1.0/logout', api_views.front.LogoutView.as_view(), name='logout'),
    url(r'^api/v1.0/register', api_views.RegistrationViewSet.as_view(), name='register'),
    url(r'^api/v1.0/password-recovery', t_auth.api.views.front.RecoveryView.as_view(), name='password-recovery'),
    url(r'^api/v1.0/', include((router.urls, 'api'), namespace='api')),
]

if settings.DEBUG:
    urlpatterns += [
        url('swagger/', TemplateView.as_view(template_name='swagger_ui.html'), name='swagger-ui'),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
