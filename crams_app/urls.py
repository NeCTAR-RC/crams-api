# coding=utf-8
"""
 URLS.py
"""
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from api.views import nectar_token_auth_view, provision_auth_token_view

urlpatterns = [
    url(r'^$', auth_views.login),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', auth_views.login),
    url(r'^api/', include('api.urls')),
    url(r'^nectar_token_auth', nectar_token_auth_view),
    url(r'^json_token_auth', provision_auth_token_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
