# coding=utf-8
"""
Database Utilities
"""
from crams.models import RequestStatus


def fetch_active_provider_object_for_user(crams_user):
    """
    fetch_active_provider_object_for_user
    :param crams_user:
    :return:
    """
    if crams_user and hasattr(crams_user, 'provider'):
        if crams_user.provider.active:
            return crams_user.provider
    return None


def get_request_status_lookups():
    """
    get_request_status_lookups
    :return:
    """
    ret_dict = {}
    for rs in RequestStatus.objects.all():
        ret_dict[rs.code] = rs
    return ret_dict
