# coding=utf-8
"""
    Test Utilities
"""
from django.forms.models import model_to_dict

__author__ = 'rafi m feroze'


def get_compute_requests_for_request(request_instance):
    """
        Get all compute request Dict for a given request instance
    :param request_instance:
    :return:
    """
    ret_list = []
    for c in request_instance.compute_requests.all():
        compute_dict = model_to_dict(c)
        compute_dict["compute_product"] = model_to_dict(c.compute_product)
        if c.provision_details:
            compute_dict['provision_details'] = \
                convert_provision_details_to_dict(c.provision_details)
        ret_list.append(compute_dict)

    return ret_list


def get_storage_requests_for_request(request_instance):
    """
        Get all storage request Dict for a given request instance
    :param request_instance:
    :return:
    """
    ret_list = []
    for s in request_instance.storage_requests.all():
        storage_dict = model_to_dict(s)
        storage_dict["storage_product"] = convert_storage_product_to_dict(
            s.storage_product)
        if s.provision_details:
            storage_dict['provision_details'] = \
                convert_provision_details_to_dict(s.provision_details)
        ret_list.append(storage_dict)

    return ret_list


def convert_storage_product_to_dict(sp_instance):
    """
        convert storage product model instance to dict
    :param sp_instance:
    :return:
    """
    ret_dict = model_to_dict(sp_instance)
    ret_dict["storage_type"] = model_to_dict(sp_instance.storage_type)
    ret_dict["funding_body"] = model_to_dict(sp_instance.funding_body)
    ret_dict['provider'] = model_to_dict(sp_instance.provider)
    if sp_instance.zone:
        ret_dict["zone"] = model_to_dict(sp_instance.zone)

    return ret_dict


def convert_provision_details_to_dict(provision_instance):
    """
        convert provision details model instance to dict
    :param provision_instance:
    :return:
    """
    ret_dict = model_to_dict(provision_instance)
    ret_dict['provider'] = model_to_dict(provision_instance.provider)
    return ret_dict
