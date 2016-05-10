# coding=utf-8
"""
    Lookup methods
"""
from collections import OrderedDict

from rest_framework.response import Response
from rest_framework.decorators import api_view

# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import AnonymousUser

from crams.models import AllocationHome, Duration, GrantType, \
    FORCode, StorageProduct, Contact
from api.v1.serializers.lookupSerializers import StorageProductSerializer

__author__ = 'simonyu, rafi m feroze'


# noinspection PyUnusedLocal
@api_view(http_method_names=['GET'])
def allocation_home(request):
    """
        get Allocaiton Home Objects as Dict
    :param request:
    :return:
    """
    allocation_homes = AllocationHome.objects.all()

    home_dict = OrderedDict()
    for alloc_home in allocation_homes:
        code = alloc_home.code
        desc = alloc_home.description
        home_dict[code] = desc
    return Response(home_dict)


# noinspection PyUnusedLocal
@api_view(http_method_names=['GET'])
def durations(request):
    """
        get Duration Objects as Dict
    :param request:
    :return:
    """
    duration_objs = Duration.objects.all()

    dur_dict = OrderedDict()
    for dur in duration_objs:
        duration = dur.duration
        label = dur.duration_label
        dur_dict[duration] = label

    return Response(dur_dict)


# noinspection PyUnusedLocal
@api_view(http_method_names=['GET'])
def grant_types(request):
    """
        get Grant Type Objects as Dict
    :param request:
    :return:
    """
    grant_type_objs = GrantType.objects.all()

    grant_type_list = []
    for grant_type in grant_type_objs:
        grant_type_list.append({'id': grant_type.id,
                                'desc': grant_type.description})
    return Response(grant_type_list)


# @api_view(http_method_names=['GET'])
# def for_codes(request):
#     for_codes = FORCode.objects.all().order_by('code')
#
#     for_codes_dict = OrderedDict()
#     for for_code in for_codes:
#         id = for_code.id
#         code = for_code.code
#         desc = for_code.description
#         for_codes_dict[id] = code + " " + desc
#
#     return Response(for_codes_dict)

# noinspection PyUnusedLocal
@api_view(http_method_names=['GET'])
def for_codes(request):
    """
        get For Code Objects as Dict
    :param request:
    :return:
    """
    for_code_objs = FORCode.objects.all().order_by('code')

    for_codes_list = []
    for for_code in for_code_objs:
        code = for_code.code
        desc = for_code.description
        for_code_dict = {'id': for_code.id, 'desc': '{} {}'.format(code, desc)}
        for_codes_list.append(for_code_dict)
    return Response(for_codes_list)


# noinspection PyUnusedLocal
@api_view(http_method_names=['GET'])
def fb_storage_product(request, searchKey):
    """
        get Storage Product Objects as Dict
    :param request:
    :return:
    """
    if not searchKey:
        searchKey = 'NeCTAR'

    nectar_sps = StorageProduct.objects.filter(
        funding_body__name__iexact=searchKey.lower()).order_by('id')

    sp_list = []
    for sp in nectar_sps:
        sp_list.append(StorageProductSerializer(sp).data)
    return Response(sp_list)


# # noinspection PyUnusedLocal
# @api_view(http_method_names=['GET'])
# def vicnode_storage_product(request):
#     """
#         Vicnode Storage Product
#     :param request:
#     :return:
#     """
#     vicnode_sps = StorageProduct.objects.filter(
#         funding_body__name='VicNode').order_by('id')
#
#     sp_list = []
#     for sp in vicnode_sps:
#         sp_list.append({'id': sp.id, 'name': sp.name})
#     return Response(sp_list)


# noinspection PyUnusedLocal
@api_view(http_method_names=['GET'])
def contacts(request):
    """
        get Contact Objects as Dict
    :param request:
    :return:
    """
    contact_objs = Contact.objects.all().order_by('given_name')

    contacts_list = []
    for contact in contact_objs:
        title = contact.title
        given_name = contact.given_name
        surname = contact.surname
        contacts_list.append(
            {'id': contact.id, 'name': '{} {} {}'.format(title,
                                                         given_name,
                                                         surname)})
    return Response(contacts_list)
