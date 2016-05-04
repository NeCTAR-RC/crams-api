# coding=utf-8
"""
    views list
"""
from functools import reduce
from json import loads as json_loads

from django.db.models import Q
from rest_framework import viewsets, permissions, generics
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_condition import And, Or  # ,ConditionalPermission, C, Not

from crams.models import Request, FundingBody
from crams.DBConstants import APPROVER_APPEND_STR
from api.serializers.requestSerializers import RequestHistorySerializer
from crams.permissions import IsRequestApprover, IsProjectContact
from api.utils import get_user_role_prefix_list

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
        print(repr(ret_dict))
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
        funding_names_of_interest = get_user_role_prefix_list(
            [APPROVER_APPEND_STR], request)
        if len(funding_names_of_interest) > 0:
            q_list1 = map(lambda n: Q(name__iexact=n),
                          [i for i in funding_names_of_interest])
            q_list = reduce(lambda a, b: a | b, [i for i in q_list1])
            for fb in FundingBody.objects.filter(q_list).order_by('name'):
                current_dict = {'id': fb.id, 'name': fb.name}
                ret_list.append(current_dict)
                current_dict[APPROVER_APPEND_STR[1:].lower()] = True
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
