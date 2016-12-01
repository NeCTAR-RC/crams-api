# coding=utf-8
"""
    Utilities to manipulate django model fields
"""
from django.core import serializers
from rest_framework import mixins, viewsets
from rest_framework import status
from rest_framework.response import Response

# noinspection PyProtectedMember
from crams import DBConstants
from crams import settings


class CramsModelViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
        A viewset similar to viewset.ModelViewSet except for destroy() action
    """

    def partial_update(self, request, *args, **kwargs):
        msg = {
            "detail": "Method \"PATCH\" not allowed."
        }
        headers = self.get_success_headers(msg)
        return Response(msg, status=status.HTTP_405_METHOD_NOT_ALLOWED,
                        headers=headers)


def list_model_fields(model_instance):
    """
        List model fields for given instance
    :param model_instance:
    """
    for f in model_instance._meta.get_all_field_names():
        print(repr(f))


# noinspection PyProtectedMember
def list_model_field_values(model_instance):
    # modify : for django 1.9 use model._meta.get_fields()  and  field.name
    """
        List model field and values for given instance
    :param model_instance:
    """
    for f in model_instance._meta.get_all_field_names():
        print(f, getattr(model_instance, f))


def get_model_field_value(model_instance, field_str):
    """
        List value for a given model field
    :param model_instance:
    :param field_str:
    :return:
    """
    return getattr(model_instance, field_str)


def json_serialize(query_set):
    """
        serialize in query_set as json
    :param query_set:
    :return:
    """
    return serializers.serialize("json", query_set)


def get_referer_host_url(request):
    base_url = None
    if request:
        base_url = request.META.get('HTTP_REFERER')
    return base_url


def generate_client_login_url(request, base_url):
    if not base_url:
        base_url = get_referer_host_url(request)

    return base_url + settings.CLIENT_KS_LOGIN_PATH


def get_funding_body_request_url(funding_body_name):
    return FUNDING_BODY_CLIENT_REQUEST_PATH.get(funding_body_name.lower())


FUNDING_BODY_CLIENT_REQUEST_PATH = {
    DBConstants.FUNDING_BODY_NECTAR.lower():
        settings.NECTAR_CLIENT_BASE_URL +
        settings.NECTAR_CLIENT_VIEW_REQUEST_PATH
}
