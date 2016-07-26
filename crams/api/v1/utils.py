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

from crams.DBConstants import ROLE_FB_MAP

__author__ = 'rafi m feroze'


def get_keystone_admin_client():
    """

   get_keystone_admin_client
    :return:
    """
    return ks_client_v3.Client(username=settings.KS_USERNAME,
                               password=settings.KS_PASSWORD,
                               project_name=settings.KS_PROJECT,
                               auth_url=settings.KS_URL)


def get_approver_role_fb_for_user(request):
    """

    :param request:
    :return:
    """

    if not hasattr(request.user, 'auth_token'):
        raise ParseError('Current user has no token, hence roles not set')

    json_roles = request.user.auth_token.cramstoken.ks_roles
    if json_roles:
        roles = set(json_loads(json_roles))
        return [ROLE_FB_MAP.get(r) for r in roles]

    return []


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
