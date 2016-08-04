# coding=utf-8
"""
 URLS.py
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from crams.api.v1 import views as api_views
from crams import views

urlpatterns = [
    url(r'^$', views.crams_root_page),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', auth_views.login),
    url(r'^nectar_token_auth', api_views.nectar_token_auth_view),
    url(r'^json_token_auth', api_views.provision_auth_token_view),
    # API Versions
    url(r'^api/v1/', include('crams.api.v1.urls', namespace='v1')),
    url(r'^api/v2/', include('crams.api.v2.urls', namespace='v2')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
