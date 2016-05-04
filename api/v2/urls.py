# coding=utf-8
"""
    URL definitions
"""
__author__ = 'rafi m feroze'  # 'mmohamed'

from django.conf.urls import include, url
from api.v2.views import not_implemented

urlpatterns = [
    url(r'^$', not_implemented),
]