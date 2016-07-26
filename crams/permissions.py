# coding=utf-8
"""
Crams Permissions
"""

from json import loads as json_loads

from rest_framework import permissions

from crams.settings import CRAMS_PROVISIONER_ROLE
from crams.roleUtils import FB_ROLE_MAP_REVERSE
from crams.models import Request, Project


def user_has_roles(userobj, role_list):
    """
    User has all given roles in the list
    :param userobj:
    :param role_list:
    :return:
    """
    role_set = set(role_list)
    if userobj and hasattr(userobj, 'auth_token'):
        auth_token = userobj.auth_token
        if hasattr(auth_token, 'cramstoken') and \
                auth_token.cramstoken.ks_roles:
            user_roles = set(json_loads(auth_token.cramstoken.ks_roles))
            return role_set.issubset(user_roles)

    return False


class IsRequestApprover(permissions.BasePermission):
    """
    Object-level permission to only allow Nectar approvers.
    """
    message = 'User does not hold Approver role for the Request.'

    def has_object_permission(self, request, view, obj):
        """
        User is an approver for given request object's funding boby
        :param request:
        :param view:
        :param obj:
        :return:
        """
        if request.user and isinstance(obj, Request):
            required_role = FB_ROLE_MAP_REVERSE.get(
                obj.funding_scheme.funding_body.name)
            if required_role:
                return user_has_roles(request.user, [required_role])
        return False


class IsActiveProvider(permissions.BasePermission):
    """
    Global permission, determine if Curent User has provider role
    """
    message = 'User does not hold Crams Provisioner role.'

    def has_permission(self, request, view):
        """
        user has CRAMS_PROVISIONER_ROLE role
        :param request:
        :param view:
        :return:
        """
        return user_has_roles(request.user, [CRAMS_PROVISIONER_ROLE])


class IsProjectContact(permissions.BasePermission):
    """
    Object-level permission to only allow reviewers of an object access to it.
    """
    message = 'User is not listed as contact for the relevant project.'

    def has_object_permission(self, request, view, obj):
        """
            User has permission to view given project or request object
        :param request:
        :param view:
        :param obj:
        :return:
        """
        project = None
        if isinstance(obj, Project):
            project = obj
        elif isinstance(obj, Request):
            project = obj.project

        if not project:
            return False

        return project.project_contacts.filter(
            contact__email=request.user.email).exists()
