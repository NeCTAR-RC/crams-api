__author__ = 'rafi m feroze'  #'mmohamed'

from rest_framework.response import Response


def not_implemented(request):
    return Response('<H3>Not implemented</H3>')