# encoding: utf-8
from django.conf import settings
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

import t_auth.api.views.front
from t_auth.api import views as api_views

router = routers.DefaultRouter()

router.register(r'login', api_views.LoginViewSet, base_name='login')
router.register(r'verify-token', api_views.VerifyTokenViewSet, base_name='verify-token')
router.register(r'register', api_views.RegistrationViewSet, base_name='register')
router.register(r'account', api_views.AccountViewSet, base_name='account')
router.register(r'account/permissions', t_auth.api.views.front.AccountPermissionsViewSet,
                base_name='account-permissions')

router.register(r'permission', t_auth.api.views.front.PermissionViewSet, base_name='permission')

# not actually used
router.register(r'check_2fa', api_views.TwoFactorViewSet, base_name='api_2fa')
router.register(r'action', api_views.ActionViewSet, base_name='api_action')

urlpatterns = [
    url(r'^api/v1.0/', include(router.urls, namespace='api')),

]
if settings.DEBUG:
    urlpatterns.append(url(r'^docs/', include_docs_urls(title='Trood Auth')))
