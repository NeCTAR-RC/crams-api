# coding=utf-8
"""
Util methods
"""
import random
import string

from json import loads as json_loads
from rest_framework.exceptions import ParseError
from itertools import chain, combinations

from keystoneclient.v3 import client as ks_client_v3
from django.conf import settings


__author__ = 'rafi m feroze'  # 'mmohamed'


def get_keystone_admin_client():
    """

   get_keystone_admin_client
    :return:
    """
    return ks_client_v3.Client(username=settings.KS_USERNAME,
                               password=settings.KS_PASSWORD,
                               project_name=settings.KS_PROJECT,
                               auth_url=settings.KEYSTONE_AUTH_URL)


def get_user_role_prefix_list(role_type_suffix_list, request):
    """
    get_user_role_prefix_list
    :param role_type_suffix_list:
    :param request:
    :return: :raise ParseError:
    """
    if not hasattr(request.user, 'auth_token'):
        raise ParseError('Current user has no token, hence roles not set')

    def get_substring_before_ends_with(ends_with_str, str_list):
        """
        get_substring_before_ends_with
        :param ends_with_str:
        :param str_list:
        :return:
        """
        return [elem.rpartition(ends_with_str)[0]
                for elem in str_list if elem.endswith(ends_with_str)]

    user_roles = []
    json_roles = request.user.auth_token.cramstoken.ks_roles
    if json_roles:
        user_roles = json_loads(json_roles)

    ret_prefix_list = []
    if len(user_roles) > 0:
        for roleStr in role_type_suffix_list:
            ret_prefix_list = ret_prefix_list + \
                get_substring_before_ends_with(roleStr, user_roles)

    return ret_prefix_list


def get_random_string(num):
    # http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python/23728630#23728630
    # return ''.join(random.choice(string.ascii_uppercase + string.digits) for
    # _ in range(num))
    """
        get_random_string
    :param num:
    :return:
    """
    return ''.join(
        random.SystemRandom().choice(
            string.ascii_uppercase +
            string.digits) for _ in range(num))

# Modified from
# http://stackoverflow.com/questions/18826571/python-powerset-of-a-given-set-with-generators


def power_set_generator(input_set):
    """
        power_set_generator
    :param input_set:
    """
    for subset in chain.from_iterable(
        combinations(
            input_set, r) for r in range(
            len(input_set) + 1)):
        yield set(subset)


def convert_list_to_frozen_set(in_list):
    """
    convert_list_to_frozen_set
    :param in_list:
    :return:
    """
    return [frozenset(i) for i in in_list]


def compare_two_lists_or_sets(s, t):
    # http://stackoverflow.com/questions/7828867/how-to-efficiently-compare-two-unordered-lists-not-sets-in-python

    """
        compare_two_lists_or_sets
    :param s:
    :param t:
    :return:
    """
    t = list(t)   # make a mutable copy
    try:
        for elem in s:
            t.remove(elem)
    except ValueError:
        return False
    return not t
