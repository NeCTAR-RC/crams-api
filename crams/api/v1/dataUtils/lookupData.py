# coding=utf-8
"""
 methods to fetch Lookup Data
"""
from rest_framework.exceptions import ParseError

from crams.models import GrantType, ProjectIDSystem, ContactRole, FORCode, \
    FundingScheme, ComputeProduct, StorageProduct, RequestStatus, Provider
from crams.api.v1.serializers.lookupSerializers import GrantTypeSerializer, \
    ProjectIDSystemSerializer, ContactRoleSerializer, FORCodeSerializer, \
    FundingSchemeSerializer, ComputeProductSerializer, \
    StorageProductSerializer, RequestStatusSerializer, ProviderSerializer

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


def get_provider_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(Provider).get_lookup_data(search_key_dict)


def get_grant_type_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(GrantType).get_lookup_data(search_key_dict)


def get_system_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(ProjectIDSystem).get_lookup_data(search_key_dict)


def get_request_status_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(RequestStatus).get_lookup_data(search_key_dict)


def get_contact_role_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(ContactRole).get_lookup_data(search_key_dict)


def get_for_code_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(FORCode).get_lookup_data(search_key_dict)


def get_funding_scheme_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(FundingScheme).get_lookup_data(search_key_dict)


def get_compute_product_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(ComputeProduct).get_lookup_data(search_key_dict)


def get_storage_product_obj(search_key_dict):
    """

    :param search_key_dict:
    :return:
    """
    return LookupDataModel(StorageProduct).get_lookup_data(search_key_dict)

# LookupData Classes


def get_provider_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = ProviderSerializer
    return LookupDataModel(Provider).serialize(search_key_dict, serializer)


def get_grant_type_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = GrantTypeSerializer
    return LookupDataModel(GrantType).serialize(search_key_dict, serializer)


def get_system_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = ProjectIDSystemSerializer
    return LookupDataModel(ProjectIDSystem).serialize(
        search_key_dict, serializer)


def get_request_status_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = RequestStatusSerializer
    return LookupDataModel(RequestStatus).serialize(search_key_dict,
                                                    serializer)


def get_contact_role_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = ContactRoleSerializer
    return LookupDataModel(ContactRole).serialize(search_key_dict,
                                                  serializer)


def get_for_code_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = FORCodeSerializer
    return LookupDataModel(FORCode).serialize(search_key_dict,
                                              serializer)


def get_funding_scheme_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = FundingSchemeSerializer
    return LookupDataModel(FundingScheme).serialize(search_key_dict,
                                                    serializer)


def get_compute_product_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = ComputeProductSerializer
    return LookupDataModel(ComputeProduct).serialize(search_key_dict,
                                                     serializer)


def get_storage_product_lookup_data(search_key_dict, serializer):
    """

    :param search_key_dict:
    :param serializer:
    :return:
    """
    if not serializer:
        serializer = StorageProductSerializer
    return LookupDataModel(StorageProduct).serialize(search_key_dict,
                                                     serializer)
