# coding=utf-8
"""
    views
"""
# import pprint
from json import dumps as json_dumps, loads as json_loads

from crams.api.v1.serializers.adminSerializers import \
    ApproveRequestModelSerializer, DeclineRequestModelSerializer, \
    ADMIN_ENABLE_REQUEST_STATUS
from crams.api.v1.serializers.projectSerializers import ProjectSerializer, \
    ContactSerializer, ContactRestrictedFieldSerializer
from crams.api.v1.serializers.provisionSerializers import \
    ProvisionRequestSerializer, ProvisionProjectSerializer, \
    UpdateProvisionProjectSerializer, PROVISION_ENABLE_REQUEST_STATUS
from crams.api.v1.serializers.requestSerializers import CramsRequestSerializer
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from keystoneclient.exceptions import ClientException
from rest_condition import And, Or  # ,ConditionalPermission, C, Not
from rest_framework import permissions, filters
from rest_framework import viewsets, generics, mixins
from rest_framework.exceptions import NotFound, AuthenticationFailed
from rest_framework.response import Response

from crams.account.models import User
from crams.DBConstants import CRAMS_NECTAR_APPROVER_ROLE, NECTARDB_APPROVER, \
    APPROVER_APPEND_STR
from crams.dbUtils import fetch_active_provider_object_for_user
from crams.models import Project, Request, Contact, Provider, CramsToken, \
    UserEvents, ProvisionDetails
from crams.permissions import IsRequestApprover, IsProjectContact, \
    IsActiveProvider
from crams.settings import CRAMS_CLIENT_COOKIE_KEY, NECTAR_CLIENT_URL
from crams.api.v1.utils import get_keystone_admin_client

__author__ = 'rafi m feroze'


@csrf_exempt
def auth_token_common(rawTokenExtractFn, request):
    """
    Specific to receive CramsToken based on input  json Keystone Token
    :param request:
    :return:
    """

    if request.method != 'POST':
        return HttpResponse('<H3>Access Denied 3<H3><BR>' + 'POST required')

    raw_token = rawTokenExtractFn()
    if not raw_token:
        raise HttpResponse('<H3>token value is required</H3>')

    try:
        client = get_keystone_admin_client()
        if not client:
            raise PermissionDenied(
                'Unable to fetch authentication details from keystone')

        user_token = client.tokens.get_token_data(raw_token)
        ks_user = user_token['token']['user']
        ks_user['roles'] = {}

        # Do not use client.role_assignments.list, we still have to go and
        # fetch project name, so go by project
        user_projects = client.projects.list(user=ks_user['id'])
        for p in user_projects:
            project_roles = client.roles.list(user=ks_user['id'],
                                              project=p)
            ks_user['roles'][p.name] = project_roles

    except ClientException as e:
        return HttpResponse('<H3>Access Denied 1<H3><BR>    - Keystone '
                            'Client: ' + str(e))

    except Exception as e:
        return HttpResponse('<H3>Access Denied 2<H3><BR>    - Keystone '
                            'Client: ' + str(e))

    return _get_crams_token_for_keystone_user(request, ks_user)


@csrf_exempt
def provision_auth_token_view(request):
    """
    Specific to receive CramsToken based on input  json Keystone Token
    :param request:
    :return:
    """
    def rawTokenExtractFn():
        json_data = request.read()
        data = json_loads(json_data.decode())
        return data.get("token", None)

    response_data = auth_token_common(rawTokenExtractFn, request)

    if isinstance(response_data, CramsToken):
        return JsonResponse({
            'token': response_data.key
        })

    return response_data


@csrf_exempt
def nectar_token_auth_view(request):
    """

    :param request:
    :return: :raise PermissionDenied:
    """

    def rawTokenExtractFn():
        return request.POST.get("token", None)

    client_url = request.COOKIES.get(CRAMS_CLIENT_COOKIE_KEY, None)
    if not client_url:
        print('No Client URL cookie, set default')
        client_url = NECTAR_CLIENT_URL
    print('client_url', NECTAR_CLIENT_URL)

    crams_token = auth_token_common(rawTokenExtractFn, request)

    username = crams_token.user.username
    query_string = "?username=%s&rest_token=%s" % (username, crams_token.key)
    if client_url:
        # redirect and authenticate user into crams
        print('redirecting...', client_url + query_string)
        print(' ---- client URL', client_url)
        response = HttpResponseRedirect(client_url + query_string)
        response['token'] = crams_token.key
        response['roles'] = crams_token.ks_roles
    else:
        print('returning to same')
        response = JsonResponse({
            'token': crams_token.key
        })

    return response


def _get_crams_token_for_keystone_user(request, ks_user):

    # look up user
    username = ks_user["name"]
    keystone_uuid = ks_user['id']
    try:
        user = User.objects.get(keystone_uuid=keystone_uuid)
        if user.email != username:
            prev_email = user.email
            user.email = username
            user.save()
            msg_format = 'User email updated from {}  to  {} for User {}'
            events = UserEvents(
                created_by=user,
                event_message=msg_format.format(repr(prev_email),
                                                repr(user.email),
                                                repr(user))
            )
            events.save()
    except User.MultipleObjectsReturned:
        raise AuthenticationFailed(
            'Multiple UserIds exist for User, contact Support')
    except User.DoesNotExist:
        try:
            user, created = User.objects.get_or_create(email=username,
                                                       username=username)
            if not user.keystone_uuid:
                user.keystone_uuid = keystone_uuid
                user.save()
            # else:
            #   error_msg = 'Invalid Keystone id in DB for User {}, \
            #                   contact Support'.format(repr(username))
            #   raise AuthenticationFailed(error_msg)

            events = UserEvents(
                created_by=user,
                event_message='User uuid set to  {} for User {}'.format(
                    repr(
                        user.keystone_uuid),
                    repr(user)))
            events.save()
        except Exception as e:
            return HttpResponse('Error creating user with email ' + username +
                                '  ' + str(e))

    # get rest token to log user in frontend
    crams_token, created = CramsToken.objects.get_or_create(user=user)
    user_roles = []
    for (project, roles) in ks_user.get("roles", {}).items():
        for r in roles:
            role = r.name.strip().lower()
            if role == NECTARDB_APPROVER:
                user_roles.append(CRAMS_NECTAR_APPROVER_ROLE)
            elif role.endswith(APPROVER_APPEND_STR):
                user_roles.append(role)
            else:
                user_roles.append(project.strip().lower() + '_' + role)

    # Temp solution
    if len(user_roles) < 1:
        user_roles.append(CRAMS_NECTAR_APPROVER_ROLE)

    # store User Roles provided by Keystone host in Crams DB,
    #      Note: session variables will not work - reDirection to external host
    crams_token.ks_roles = json_dumps(user_roles)

    try:
        crams_token.save()
    except Exception as e:
        return HttpResponse('<H3>Access Denied<H3><BR>' + str(e))

    return crams_token


class RequestViewSet(viewsets.ModelViewSet):
    """
    class RequestViewSet
    """
    permission_classes = [
        And(permissions.IsAuthenticated,
            Or(IsProjectContact, IsRequestApprover))]
    queryset = Request.objects.filter(parent_request__isnull=True)
    serializer_class = CramsRequestSerializer

    def list(self, request, **kwargs):
        """
        list
        :param request:
        :param kwargs:
        :return:
        """
        request_id = request.query_params.get('request_id', None)
        if request_id:
            queryset = Project.objects.filter(
                requests__id=request_id).distinct()
        else:
            # noinspection PyPep8
            queryset = Request.objects.filter(
                project__project_contacts__contact__email=self.request.user.email,
                parent_request__isnull=True).distinct()
        serializer = CramsRequestSerializer(queryset, many=True)
        return Response(serializer.data)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    class ProjectViewSet
    """
    permission_classes = [
        And(permissions.IsAuthenticated, Or(IsProjectContact))]
    queryset = Project.objects.all()  # filter(parent_project__isnull=True)
    serializer_class = ProjectSerializer

    #    def filter_queryset(self, queryset): #for List
    # return
    # queryset.filter(project_contacts__contact__email=self.request.user.email,
    # parent_project__isnull=False).distinct()

    def list(self, request, **kwargs):
        """
        list
        :param request:
        :param kwargs:
        :return:
        """
        request_id = request.query_params.get('request_id', None)
        if request_id:
            queryset = Project.objects.filter(
                requests__id=request_id).distinct()
        else:
            queryset = Project.objects.filter(
                project_contacts__contact__email=self.request.user.email,
                parent_project__isnull=True).distinct()
        serializer = ProjectSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)


class ContactViewSet(viewsets.ModelViewSet):
    """
    class ContactViewSet
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class ContactDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    """
    class ContactDetail
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    lookup_field = 'email'

    def get(self, request, *args, **kwargs):
        """
            get
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return self.retrieve(request, *args, **kwargs)


class SearchContact(generics.ListAPIView):
    """
    class SearchContact
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = ContactRestrictedFieldSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('given_name', 'surname', 'email')


class ApproveRequestViewSet(viewsets.ModelViewSet):
    """
    class ApproveRequestViewSet
    """
    permission_classes = (permissions.IsAuthenticated, IsRequestApprover)
    serializer_class = ApproveRequestModelSerializer
    queryset = Request.objects.filter(
        parent_request__isnull=True,
        request_status__code__in=ADMIN_ENABLE_REQUEST_STATUS)


class DeclineRequestViewSet(viewsets.ModelViewSet):
    """
    class DeclineRequestViewSet
    """
    permission_classes = (permissions.IsAuthenticated, IsRequestApprover)
    serializer_class = DeclineRequestModelSerializer
    queryset = Request.objects.filter(
        parent_request__isnull=True,
        request_status__code__in=ADMIN_ENABLE_REQUEST_STATUS)


class UpdateProvisionProjectViewSet(viewsets.ModelViewSet):
    """
    class UpdateProvisionProjectViewSet
    """
    permission_classes = (permissions.IsAuthenticated, IsActiveProvider)
    serializer_class = UpdateProvisionProjectSerializer
    queryset = Project.objects.filter(
        parent_project__isnull=True,
        requests__parent_request__isnull=True,
        requests__request_status__code__in=PROVISION_ENABLE_REQUEST_STATUS)

    # noinspection PyProtectedMember
    def list(self, request, **kwargs):
        """
        list
        :param request:
        :param kwargs:
        :return:
        """
        return Response(
            UpdateProvisionProjectSerializer()._init_empty(
                'Sample ', 1))


class ProvisionProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    class ProvisionProjectViewSet
    """
    permission_classes = (permissions.IsAuthenticated, IsActiveProvider)
    serializer_class = ProvisionProjectSerializer
    queryset = Project.objects.filter(
        parent_project__isnull=True, requests__parent_request__isnull=True,
        requests__request_status__code__in=PROVISION_ENABLE_REQUEST_STATUS)

    def filter_queryset(self, queryset):  # for List
        """
        filter_queryset
        :param queryset:
        :return: :raise NotFound:
        """
        crams_user = self.request.user
        if not Provider.is_provider(crams_user):
            raise NotFound('User does not have a provider Role')

        valid_provider = fetch_active_provider_object_for_user(crams_user)
        if not valid_provider:
            raise NotFound('User {} does not have an active provider Role'.
                           format(repr(crams_user)))
        # noinspection PyPep8
        provider_filter = Q(
            requests__compute_requests__compute_product__provider=valid_provider) | Q(
            requests__storage_requests__storage_product__provider=valid_provider)
        # noinspection PyPep8
        exclude_filter = Q(
            linked_provisiondetails__provision_details__status=ProvisionDetails.FAILED)
        return queryset.filter(provider_filter).\
            exclude(exclude_filter).all().distinct()


class ProvisionRequestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    class ProvisionRequestViewSet
    """
    permission_classes = (permissions.IsAuthenticated, IsActiveProvider)
    serializer_class = ProvisionRequestSerializer
    queryset = Request.objects.filter(
        request_status__code__in=PROVISION_ENABLE_REQUEST_STATUS,
        parent_request__isnull=True,
    )

    def filter_queryset(self, queryset):  # for List
        """
        filter_queryset
        :param queryset:
        :return: :raise NotFound:
        """
        crams_user = self.request.user
        if not Provider.is_provider(crams_user):
            raise NotFound('User does not have a provider Role')

        valid_provider = fetch_active_provider_object_for_user(crams_user)
        provider_filter = Q(
            compute_requests__compute_product__provider=valid_provider) | Q(
            storage_requests__storage_product__provider=valid_provider)
        return queryset.filter(provider_filter).distinct()
