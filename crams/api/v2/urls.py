# coding=utf-8
"""
    URL definitions
"""

from django.conf.urls import url
from crams.api.v2.views import not_implemented

__author__ = 'rafi m feroze'

urlpatterns = [
    url(r'^$', not_implemented),
]
