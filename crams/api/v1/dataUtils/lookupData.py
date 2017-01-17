# coding=utf-8
"""
 methods to fetch Lookup Data
"""
from rest_framework.exceptions import ParseError

from crams import models

from crams.api.v1.serializers import lookupSerializers

__author__ = 'Rafi M Feroze'


class LookupDataModel:

    """

    :param model:
    """

    def __init__(self, model):
        self.model = model

    def get_lookup_data(self, search_key_dict):
        """

        :param search_key_dict:
        :return: :raise ParseError:
        """
        try:
            return self.model.objects.get(**search_key_dict)
        except self.model.DoesNotExist:
            raise ParseError(self.model.__name__ +
                             ' does not exist for search_key_dict ' +
                             repr(search_key_dict))
        except self.model.MultipleObjectsReturned:
            raise ParseError(self.model.__name__ +
                             ' Multiple objects found for search_key_dict ' +
                             repr(search_key_dict))

    def serialize(self, search_key_dict, serializer):
        """

        :param search_key_dict:
        :param serializer:
        :return: :raise ParseError:
        """
        try:
            return serializer(self.get_lookup_data(search_key_dict)).data
        except Exception:
            raise ParseError(
                self.model.__name__ + ': error serializing data for search' +
                                      '_key_dict ' + repr(search_key_dict))


def get_allocation_home_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(models.AllocationHome).\
        get_lookup_data(search_key_dict)


def get_provider_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(models.Provider).get_lookup_data(search_key_dict)


def get_grant_type_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(models.GrantType).get_lookup_data(search_key_dict)


def get_system_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(models.ProjectIDSystem).\
        get_lookup_data(search_key_dict)


def get_request_status_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(models.RequestStatus).\
        get_lookup_data(search_key_dict)


def get_contact_role_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(models.ContactRole).\
        get_lookup_data(search_key_dict)


def get_for_code_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(models.FORCode).\
        get_lookup_data(search_key_dict)


def get_funding_scheme_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(models.FundingScheme).\
        get_lookup_data(search_key_dict)


def get_compute_product_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(models.ComputeProduct).\
        get_lookup_data(search_key_dict)


def get_storage_product_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(models.StorageProduct).\
        get_lookup_data(search_key_dict)


# LookupData Classes
def get_allocation_home_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = lookupSerializers.AllocationHomeSerializer
    return LookupDataModel(models.AllocationHome).\
        serialize(search_key_dict, serializer)


def get_provider_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = lookupSerializers.ProviderSerializer
    return LookupDataModel(models.Provider).\
        serialize(search_key_dict, serializer)


def get_grant_type_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = lookupSerializers.GrantTypeSerializer
    return LookupDataModel(models.GrantType).\
        serialize(search_key_dict, serializer)


def get_system_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = lookupSerializers.ProjectIDSystemSerializer
    return LookupDataModel(models.ProjectIDSystem).serialize(
        search_key_dict, serializer)


def get_request_status_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = lookupSerializers.RequestStatusSerializer
    return LookupDataModel(models.RequestStatus).\
        serialize(search_key_dict, serializer)


def get_contact_role_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = lookupSerializers.ContactRoleSerializer
    return LookupDataModel(models.ContactRole).\
        serialize(search_key_dict, serializer)


def get_for_code_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = lookupSerializers.FORCodeSerializer
    return LookupDataModel(models.FORCode).\
        serialize(search_key_dict, serializer)


def get_funding_scheme_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = lookupSerializers.FundingSchemeSerializer
    return LookupDataModel(models.FundingScheme).\
        serialize(search_key_dict, serializer)


def get_compute_product_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = lookupSerializers.ComputeProductSerializer
    return LookupDataModel(models.ComputeProduct).\
        serialize(search_key_dict, serializer)


def get_storage_product_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = lookupSerializers.StorageProductSerializer
    return LookupDataModel(models.StorageProduct).\
        serialize(search_key_dict, serializer)
