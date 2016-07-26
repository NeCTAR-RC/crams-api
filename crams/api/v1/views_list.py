# coding=utf-8
"""
    views list
"""
from json import loads as json_loads

from crams.api.v1.serializers.requestSerializers import \
     RequestHistorySerializer
from rest_condition import And, Or
from rest_framework import viewsets, permissions, generics
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from crams.models import Request, FundingBody
from crams.permissions import IsRequestApprover, IsProjectContact
from crams.api.v1.utils import get_authorised_funding_bodies
from crams.DBConstants import JSON_APPROVER_STR

__author__ = 'rafi m feroze'


class CurrentUserRolesView(generics.RetrieveAPIView):
    """
        current user roles view
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user = request.user
        ret_dict = {'roles': []}
        if user.auth_token and user.auth_token.cramstoken \
                and user.auth_token.cramstoken.ks_roles:
            ret_dict['roles'] = json_loads(user.auth_token.cramstoken.ks_roles)
        ret_dict['user'] = {'name': user.get_full_name(), 'email': user.email}
        return Response(ret_dict)


class CurrentUserApproverRoleList(viewsets.ViewSet):
    """
     current user approver role list
    """
    permission_classes = [permissions.IsAuthenticated]

    # noinspection PyMethodMayBeStatic
    def list(self, request):
        """
            List
        :param request:
        :return:
        """
        ret_list = []
        fb_name_list = get_authorised_funding_bodies(request.user)
        if len(fb_name_list) > 0:
            for fb in FundingBody.objects.filter(
                    name__iregex=r'(' + '|'.join(fb_name_list) + ')'):
                current_dict = {'id': fb.id, 'name': fb.name}
                ret_list.append(current_dict)
                current_dict[JSON_APPROVER_STR] = True
        return Response(ret_list)


class RequestHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
        request history view set
    """
    serializer_class = RequestHistorySerializer
    permission_classes = [
        And(permissions.IsAuthenticated,
            Or(IsProjectContact, IsRequestApprover))]

    def get_queryset(self):
        """
            get queryset
        :return: :raise ParseError:
        """
        request_id = self.request.query_params.get('request_id', None)
        if not request_id:
            raise ParseError('Request Id parameter is required')

        try:
            request = Request.objects.get(pk=request_id)
            ret_list = []
            if request.history:
                ret_list = list(request.history.all())
            elif request.parent_request:
                ret_list = list(request.parent_request.history.all())

            ret_list.append(request)
            return ret_list

        except Request.DoesNotExist:
            raise ParseError(
                'Request not found for Id {}'.format(repr(request_id)))
