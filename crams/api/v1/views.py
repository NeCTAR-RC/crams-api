# coding=utf-8
"""
    views
"""
from json import loads as json_loads

from crams.api.v1.serializers.adminSerializers import \
    ApproveRequestModelSerializer, DeclineRequestModelSerializer, \
    ADMIN_ENABLE_REQUEST_STATUS
from crams.api.v1.serializers.projectSerializers import ProjectSerializer, \
    ContactSerializer, ContactRestrictedFieldSerializer
from crams.api.v1.serializers.provisionSerializers import \
    ProvisionRequestSerializer, ProvisionProjectSerializer, \
    UpdateProvisionProjectSerializer, PROVISION_ENABLE_REQUEST_STATUS
from crams.api.v1.serializers.requestSerializers import CramsRequestSerializer
from django.core import exceptions
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from keystoneclient.exceptions import ClientException
from rest_condition import And, Or
from rest_framework import filters
from rest_framework import viewsets, generics, mixins
from rest_framework import exceptions as rest_exceptions
from rest_framework.response import Response

from crams.account.models import User
from crams.lang_utils import strip_lower
from crams import dbUtils
from crams.models import Project, Request, Contact, Provider, CramsToken
from crams.models import UserEvents
from crams.permissions import IsRequestApprover, IsProjectContact
from crams import settings
from crams.permissions import IsActiveProvider, IsCramsAuthenticated
from crams.api.v1.utils import get_keystone_admin_client
from crams import roleUtils
from crams import django_utils


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
            raise exceptions.PermissionDenied(
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
    def raw_token_extract_fn():
        json_data = request.read()
        data = json_loads(json_data.decode())
        return data.get("token", None)

    response_data = auth_token_common(raw_token_extract_fn, request)

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

    def raw_token_extract_fn():
        return request.POST.get("token", None)

    client_login_url = request.COOKIES.get(settings.CRAMS_CLIENT_COOKIE_KEY)
    if not client_login_url:
        client_login_url = django_utils.generate_client_login_url(
            request, settings.NECTAR_CLIENT_BASE_URL)

    crams_token = auth_token_common(raw_token_extract_fn, request)
    if not isinstance(crams_token, CramsToken):
        if isinstance(crams_token, HttpResponse):
            return crams_token
        raise exceptions.PermissionDenied(
            'Error fetching Keystone token {}'.format(repr(crams_token)))

    username = crams_token.user.username
    query_string = "?username=%s&rest_token=%s" % (username, crams_token.key)
    if client_login_url:
        # redirect and authenticate user into crams
        response = HttpResponseRedirect(client_login_url + query_string)
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
    keystone_id = ks_user['id']
    try:
        user = User.objects.get(keystone_uuid=keystone_id)

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
        raise rest_exceptions.AuthenticationFailed(
            'Multiple UserIds exist for User, contact Support')
    except User.DoesNotExist:
        try:
            user, created = User.objects.get_or_create(email=username,
                                                       username=username)
            if not user.keystone_uuid:
                user.keystone_uuid = keystone_id
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

    # Expire existing Token and log Login
    if hasattr(user, 'auth_token'):
        user.auth_token.delete()
    msg = 'User logged in with valid Keystone token'
    events = UserEvents(
        created_by=user,
        event_message=msg
    )
    events.save()

    configurable_roles = roleUtils.get_configurable_roles()
    user_roles = []
    for (project, roles) in ks_user.get("roles", {}).items():
        for role_obj in roles:
            role = strip_lower(role_obj.name)
            if role in configurable_roles:
                user_roles.append(role)
            else:
                p_role = roleUtils.generate_project_role(project, role)
                if p_role not in configurable_roles:  # additional security
                    user_roles.append(p_role)

    return roleUtils.setup_case_insensitive_roles(user, user_roles)


class AbstractCramsRequestViewSet(django_utils.CramsModelViewSet):
    def __init__(self, **kwargs):
        self.crams_object_level = False
        super().__init__(**kwargs)

    def get_object(self):
        self.crams_object_level = True
        return super().get_object()

    def get_queryset(self):
        """

        :return:
        """
        def get_project_contact_filter(data):
            q_obj = Q(project_contacts__contact__email=data.email)
            if not self.crams_object_level:
                q_obj = q_obj & Q(parent_project__isnull=True)
            return q_obj

        def get_request_contact_filter(data):
            q_obj = Q(project__project_contacts__contact__email=data.email)
            if not self.crams_object_level:
                q_obj = q_obj & Q(parent_request__isnull=True,
                                  project__parent_project__isnull=True)
            return q_obj

        def get_project_request_id_filter(data):
            f_l = data.user_fb_list
            c_q = Q(project_contacts__contact__email=data.email)
            if f_l:
                c_q = c_q | Q(requests__funding_scheme__funding_body__in=f_l)
            return Q(requests__id=data.request_id) & c_q

        def get_request_id_filter(data):
            fb_list = data.user_fb_list
            c_q = Q(project__project_contacts__contact__email=data.email)
            if fb_list:
                c_q = c_q | Q(funding_scheme__funding_body__in=fb_list)
            return Q(id=data.request_id) & c_q

        class TempObject(object):
            user_obj = self.request.user
            email = user_obj.email
            user_fb_list = dbUtils.get_fb_obj_for_fb_names(
                roleUtils.fetch_user_role_fb_list(user_obj))
            request_id = self.request.query_params.get('request_id', None)

        queryset = self.queryset
        qs_filter = Q(id__isnull=True)  # exclude everything by default

        data = TempObject()
        if data.request_id and data.request_id.isnumeric():
            if queryset.model is Project:
                qs_filter = get_project_request_id_filter(data)
            elif queryset.model is Request:
                qs_filter = get_request_id_filter(data)
        else:
            if queryset.model is Project:
                qs_filter = get_project_contact_filter(data)
            elif queryset.model is Request:
                qs_filter = get_request_contact_filter(data)

        if (data.request_id or self.crams_object_level) and \
                not queryset.filter(qs_filter).exists():
            raise exceptions.PermissionDenied()

        return queryset.filter(qs_filter).distinct()


class RequestViewSet(AbstractCramsRequestViewSet):
    """
    class RequestViewSet
    """
    permission_classes = [
        And(IsCramsAuthenticated,
            Or(IsProjectContact, IsRequestApprover))]
    queryset = Request.objects.all()
    serializer_class = CramsRequestSerializer
    ordering_fields = ('project', 'creation_ts')
    ordering = ('project', '-creation_ts')


class ProjectViewSet(AbstractCramsRequestViewSet):
    """
    class ProjectViewSet
    """
    permission_classes = (IsCramsAuthenticated, IsProjectContact)
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    ordering_fields = ('title', 'creation_ts')
    ordering = ('title', '-creation_ts')


class ContactViewSet(django_utils.CramsModelViewSet):
    """
    class ContactViewSet
    """
    permission_classes = [IsCramsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class ContactDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    """
    class ContactDetail
    """
    permission_classes = [IsCramsAuthenticated]
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
    permission_classes = [IsCramsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = ContactRestrictedFieldSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('given_name', 'surname', 'email')


class ApproveRequestViewSet(django_utils.CramsModelViewSet):
    """
    class ApproveRequestViewSet
    """
    permission_classes = (IsCramsAuthenticated, IsRequestApprover)
    serializer_class = ApproveRequestModelSerializer
    queryset = Request.objects.filter(
        parent_request__isnull=True,
        request_status__code__in=ADMIN_ENABLE_REQUEST_STATUS)


class DeclineRequestViewSet(django_utils.CramsModelViewSet):
    """
    class DeclineRequestViewSet
    """
    permission_classes = (IsCramsAuthenticated, IsRequestApprover)
    serializer_class = DeclineRequestModelSerializer
    queryset = Request.objects.filter(
        parent_request__isnull=True,
        request_status__code__in=ADMIN_ENABLE_REQUEST_STATUS)


class UpdateProvisionProjectViewSet(django_utils.CramsModelViewSet):
    """
    class UpdateProvisionProjectViewSet
    """
    permission_classes = (IsCramsAuthenticated, IsActiveProvider)
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


class AbstractListProvisionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsCramsAuthenticated, IsActiveProvider)

    def filter_queryset(self, queryset):  # for List
        """
        filter_queryset
        :param queryset:
        :return: :raise NotFound:
        """
        return self.filter_provision_view_queryset(queryset)

    def filter_provision_view_queryset(self, queryset):
        crams_user = self.request.user
        if not Provider.is_provider(crams_user):
            msg = 'User does not have a provider Role'
            raise rest_exceptions.NotFound(msg)

        valid_provider = dbUtils.fetch_active_provider_object_for_user(
            crams_user)
        if not valid_provider:
            msg = 'User {} does not have an active provider Role'
            raise rest_exceptions.NotFound(msg.format(repr(crams_user)))
        vp = valid_provider

        if queryset.model is Project:
            provider_filter = \
                Q(requests__compute_requests__compute_product__provider=vp) | \
                Q(requests__storage_requests__storage_product__provider=vp)
        elif queryset.model is Request:
            provider_filter = \
                Q(compute_requests__compute_product__provider=valid_provider) \
                | Q(storage_requests__storage_product__provider=valid_provider)

        return queryset.filter(provider_filter).distinct()


class ProvisionProjectViewSet(AbstractListProvisionViewSet):
    """
    class ProvisionProjectViewSet
    """
    permission_classes = (IsCramsAuthenticated, IsActiveProvider)
    serializer_class = ProvisionProjectSerializer
    queryset = Project.objects.filter(
        parent_project__isnull=True, requests__parent_request__isnull=True,
        requests__request_status__code__in=PROVISION_ENABLE_REQUEST_STATUS)


class ProvisionRequestViewSet(AbstractListProvisionViewSet):
    """
    class ProvisionRequestViewSet
    """
    permission_classes = (IsCramsAuthenticated, IsActiveProvider)
    serializer_class = ProvisionRequestSerializer
    queryset = Request.objects.filter(
        request_status__code__in=PROVISION_ENABLE_REQUEST_STATUS,
        parent_request__isnull=True,
    )
