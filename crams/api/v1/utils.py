# coding=utf-8
"""
Util methods
"""
import random
import string
import itertools

from django.conf import settings
from keystoneclient.v3 import client as ks_client_v3


def get_keystone_admin_client():
    """

   get_keystone_admin_client
    :return:
    """
    return ks_client_v3.Client(username=settings.KS_USERNAME,
                               password=settings.KS_PASSWORD,
                               project_name=settings.KS_PROJECT,
                               auth_url=settings.KS_URL)


def generate_all_case_combinations(some_str):
    # Reference: http://stackoverflow.com/questions/11144389/find-all-upper
    # -lower-and-mixed-case-combinations-of-a-string
    return \
        map(''.join, itertools.product(*zip(some_str.upper(),
                                            some_str.lower())))


def get_random_string(num):
    # http://stackoverflow.com/questions/2257441/random-string-generation-with
    # -upper-case-letters-and-digits-in-python/23728630#23728630
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
    for subset in itertools.chain.from_iterable(
        itertools.combinations(
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
