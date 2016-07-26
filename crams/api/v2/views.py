from django.http import HttpResponse

__author__ = 'rafi m feroze'


def not_implemented(request):
    return HttpResponse('<H3>Not implemented</H3>')
