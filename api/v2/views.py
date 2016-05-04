__author__ = 'rafi m feroze'  #'mmohamed'

from django.http import HttpResponse


def not_implemented(request):
    return HttpResponse('<H3>Not implemented</H3>')