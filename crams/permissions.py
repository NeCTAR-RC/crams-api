# coding=utf-8
"""
Crams Permissions
"""

from rest_framework import permissions, exceptions

from crams.settings import CRAMS_PROVISIONER_ROLE, TOKEN_EXPIRY_TIME_SECONDS
from crams.roleUtils import FB_ROLE_MAP_REVERSE, fetch_cramstoken_roles
from crams.models import Request, Project, CramsToken
from crams.lang_utils import strip_lower
from crams.dateUtils import get_current_time_for_app_tz, get_seconds_elapsed


def user_has_roles(userobj, role_list):
    """
    User has all given roles in the list
    :param userobj:
    :param role_list:
    :return:
    """
    role_set = set([strip_lower(role) for role in role_list])
    user_roles = fetch_cramstoken_roles(userobj)
    if user_roles:
        return role_set.issubset(fetch_cramstoken_roles(userobj))

    return False


class IsCramsAuthenticated(permissions.IsAuthenticated):
    """
    Global permission, determine if Curent User has provider role
    """
    message = 'User does not hold valid CramsToken.'

    def has_permission(self, request, view):
        """
        user has a valid cramstoken (not expired)
        :param request:
        :param view:
        :return:
        """
        if super().has_permission(request, view):
            crams_token = CramsToken.objects.get(user=request.user)
            elapsed_seconds = get_seconds_elapsed(
                get_current_time_for_app_tz(), crams_token.created)
            if elapsed_seconds >= TOKEN_EXPIRY_TIME_SECONDS:
                raise exceptions.NotAuthenticated(self.message)
            return True

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
