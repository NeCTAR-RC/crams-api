# coding=utf-8
"""
    URL definitions
"""

from django.conf.urls import url
from api.v2.views import not_implemented

__author__ = 'rafi m feroze'  # 'mmohamed'

urlpatterns = [
    url(r'^$', not_implemented),
]
