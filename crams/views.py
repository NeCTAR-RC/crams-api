# coding=utf-8
"""
Views related to Crams Model
"""
from django.contrib.auth.decorators import login_required
from json import loads as json_loads, dumps as json_dumps
from django.http import HttpResponse

from crams.DBConstants import APPROVER_APPEND_STR, CRAMS_PROVISIONER_ROLE
from crams.models import Provider
from crams.settings import DEBUG_APPROVERS, APP_ENV
# Create your views here.


def _add_debug_role(user, new_role):
    if user.email in DEBUG_APPROVERS and APP_ENV == 'DEV':
        if user.auth_token and user.auth_token.cramstoken:
            cramstoken = user.auth_token.cramstoken
            if cramstoken.ks_roles:
                ks_roles = json_loads(cramstoken.ks_roles)
            else:
                ks_roles = []

            ks_roles_set = set(ks_roles)
            ks_roles_set.add(new_role)
            cramstoken.ks_roles = json_dumps(list(ks_roles_set))
            cramstoken.save()
            return HttpResponse('<H3>Role Added <H3><BR>' + new_role)

    return HttpResponse('<H3>Access Denied - cannot add role<H3><BR>')


@login_required
def debug_add_approver_role(request, fb_name):
    """
    Temporarily add approver role for Debug purposes
    :param request:
    :param fb_name:
    :return:
    """
    if fb_name:
        new_role = fb_name.strip().lower() + APPROVER_APPEND_STR
        user = request.user
        return _add_debug_role(user, new_role)


@login_required
def debug_add_provisioner_role(request):
    """
    Temporarily add provisioner role for Debug purposes,
    :param request:
    :return:
    """
    user = request.user
    if not hasattr(user, 'provider'):
        provider_name = 'Debug Provider - ' + user.username
        p = Provider(name=provider_name, crams_user=user)
        p.save()

    new_role = CRAMS_PROVISIONER_ROLE
    return _add_debug_role(user, new_role)
