# encoding: utf-8
from django.conf import settings
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from t_auth.api import views as api_views

router = routers.DefaultRouter()

router.register(r'login', api_views.LoginViewSet, base_name='login')
router.register(r'check-token', api_views.AuthViewSet, base_name='auth')
router.register(r'register', api_views.RegistrationViewSet, base_name='register')
router.register(r'permission', api_views.PermissionViewSet, base_name='permission')
router.register(r'user', api_views.UserViewSet, base_name='user')

# not actually used
router.register(r'check_2fa', api_views.TwoFactorViewSet, base_name='api_2fa')
router.register(r'action', api_views.ActionViewSet, base_name='api_action')

urlpatterns = [
    url(r'^api/v1.0/', include(router.urls, namespace='api')),

]
if settings.DEBUG:
    urlpatterns.append(url(r'^docs/', include_docs_urls(title='Trood Auth')))
