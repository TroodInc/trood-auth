# encoding: utf-8
from django.conf import settings
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

import t_auth.api.views.front
import t_auth.api.views.system
from t_auth.api import views as api_views
from t_auth.api.views.admin import AccountRoleViewSet

router = routers.DefaultRouter()

router.register(r'login', api_views.LoginViewSet, base_name='login')
router.register(r'register', api_views.RegistrationViewSet, base_name='register')
router.register(r'account', api_views.AccountViewSet, base_name='account')

router.register(r'endpoints', t_auth.api.views.admin.EndpointsViewSet, base_name='endpoints')
router.register(r'permissions', t_auth.api.views.admin.PermissionViewSet, base_name='permissions')

# not actually used
router.register(r'check_2fa', api_views.TwoFactorViewSet, base_name='api_2fa')

router.register(r'roles', AccountRoleViewSet, base_name='roles')

urlpatterns = [
    url(r'^api/v1.0/logout', api_views.front.LogoutView.as_view(), name='logout'),
    url(r'^api/v1.0/verify-token', t_auth.api.views.system.VerifyTokenView.as_view(), name='verify-token'),
    url(r'^api/v1.0/invalidate-token', t_auth.api.views.system.InvalidateTokenView.as_view(), name='invalidate-token'),
    url(r'^api/v1.0/', include(router.urls, namespace='api')),

]
if settings.DEBUG:
    urlpatterns.append(url(r'^docs/', include_docs_urls(title='Trood Auth')))
