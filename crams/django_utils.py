# coding=utf-8
"""
    Utilities to manipulate django model fields
"""
from django.core import serializers

__author__ = 'rafi m feroze'


# noinspection PyProtectedMember
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
