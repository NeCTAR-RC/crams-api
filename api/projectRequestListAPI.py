# coding=utf-8
"""
 project request lost APIs
"""
from django.db.models import Q
from api.utils import get_user_role_prefix_list

from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from crams.models import Project, Request, FundingBody
from crams.DBConstants import APPROVER_APPEND_STR
from api.serializers.requestSerializers import ComputeRequestSerializer
from api.serializers.requestSerializers import StorageRequestSerializer
from api.serializers.lookupSerializers import UserSerializer
from api import APIConstants
from collections import OrderedDict
from api.serializers.utilitySerializers import ProvisionDetailsSerializer
import datetime

__author__ = 'rafi m feroze, Simon Yu'


def get_funding_schemes_for_api_request(request, role_type_append_list):
    """
        get_funding_schemes_for_api_request
    :param request:
    :param role_type_append_list:
    :return: :raise ParseError:
    """
    funding_body_name_list = get_user_role_prefix_list(
        role_type_append_list, request)

    funding_schemes = set()
    requested_funding_id = request.query_params.get('funding_body_id', None)

    if requested_funding_id:
        try:
            requested_fb = FundingBody.objects.get(pk=requested_funding_id)
            if requested_fb.name.strip().lower() in funding_body_name_list:
                funding_schemes.update(requested_fb.funding_schemes.all())
            else:
                raise ParseError('User does not have {} access to {}'.format(
                    'Approver', requested_fb.name))
        except FundingBody.DoesNotExist:
            raise ParseError('Funding body does not exist for id {}'.format(
                repr(requested_funding_id)))

    else:
        for fb in FundingBody.objects.all():
            if fb.name.strip().lower() in funding_body_name_list:
                funding_schemes.update(fb.funding_schemes.all())

    return funding_schemes


class FundingBodyAllocationsCounter(APIView):
    """
        FundingBodyAllocationsCounter
    """
    permission_classes = [IsAuthenticated]

    # noinspection PyUnusedLocal
    def get(self, request, format=None):
        """
            Get
        :param request:
        :param format:
        :return:
        """
        ret_dict = {}
        user_funding_schemes = get_funding_schemes_for_api_request(
            request, [APPROVER_APPEND_STR])

        # status_params = request.query_params.get('req_status', None)
        # if status_params:
        #     req_status = status_params

        if user_funding_schemes:
            projects_dict = query_projects(user_funding_schemes, 'new')
            counter_new = len(projects_dict)

            projects_dict = query_projects(user_funding_schemes, 'approved')
            counter_approved = len(projects_dict)

            projects_dict = query_projects(user_funding_schemes, 'active')
            counter_active = len(projects_dict)

            projects_dict = query_projects(user_funding_schemes, 'expired')
            counter_expired = len(projects_dict)
            status_counter = {
                'new': counter_new,
                "approved": counter_approved,
                "active": counter_active,
                "expired": counter_expired}
            return Response({'counter': status_counter})

        return Response(ret_dict)


class ApproverReviewerRequestListView(APIView):
    """
        class ApproverReviewerRequestListView
    """
    permission_classes = [IsAuthenticated]

    # noinspection PyUnusedLocal
    def get(self, request, format=None):
        """
            get
        :param request:
        :param format:
        :return:
        """
        ret_dict = {}
        user_funding_schemes = get_funding_schemes_for_api_request(
            request, [APPROVER_APPEND_STR])

        status_params = request.query_params.get('req_status', None)
        req_status = 'new'
        if status_params:
            req_status = status_params

        if user_funding_schemes:
            projects_dict = query_projects(user_funding_schemes, req_status)
            return _populate_projects_response(request, projects_dict, True)

        return Response(ret_dict)


def query_projects(user_funding_schemes, req_status):
    """
        query_projects
    :param user_funding_schemes:
    :param req_status:
    :return:
    """
    requests = []

    if req_status.lower() == APIConstants.REQ_NEW:
        requests = Request.objects.filter(
            funding_scheme__in=user_funding_schemes, request_status__code__in=[
                'E', 'X'], parent_request__isnull=True)\
            .order_by('project__title')
    if req_status.lower() == APIConstants.REQ_APPROVED:
        requests = Request.objects.filter(
            funding_scheme__in=user_funding_schemes,
            request_status__code='A',
            parent_request__isnull=True).order_by('project__title')

    curent_date = datetime.datetime.now().strftime("%Y-%m-%d")
    if req_status.lower() == APIConstants.REQ_ACTIVE:
        requests = Request.objects.filter(
            Q(
                funding_scheme__in=user_funding_schemes) & Q(
                request_status__code='P') & Q(
                end_date__gte=curent_date) & (
                    Q(
                        parent_request__isnull=True) | ~Q(
                            parent_request__request_status__code='P')))\
            .order_by('project__title')
    if req_status.lower() == APIConstants.REQ_EXPIRY:
        requests = Request.objects.filter(
            Q(
                funding_scheme__in=user_funding_schemes) & Q(
                request_status__code='P') & Q(
                end_date__lt=curent_date) & (
                    Q(
                        parent_request__isnull=True) | ~Q(
                            parent_request__request_status__code='P')))\
            .order_by('project__title')

    projects_dict = OrderedDict()

    for crams_request in requests:
        crams_proj = crams_request.project
        populate_projects_dict(projects_dict, crams_proj, crams_request)

    return projects_dict


def populate_projects_dict(projects_dict, crams_project, crams_request):
    """
        populate_projects_dict
    :param projects_dict:
    :param crams_project:
    :param crams_request:
    """
    proj_id = crams_project.id
    found_project = projects_dict.get(proj_id)
    # if a project contains many request, we have to append all requests in it
    if found_project is None:
        projects_dict[proj_id] = {
            'project': crams_project, 'requests': [crams_request]}
    else:
        found_project['requests'].append(crams_request)


def _populate_projects_response(request, projects_dict, include_request_flag):
    ret_dict = {}
    ret_dict['user'] = UserSerializer(request.user).data

    project_list = []
    ret_dict['projects'] = project_list

    for key in projects_dict.keys():

        proj_dict = projects_dict.get(key)
        proj = proj_dict['project']
        reqs = proj_dict['requests']

        pd_list = []
        for ppd in proj.linked_provisiondetails.all():
            pd_data = ProvisionDetailsSerializer(ppd.provision_details).data
            pd_list.append(pd_data)

        project_dict = {}
        project_list.append(project_dict)
        project_dict['title'] = proj.title
        project_dict['id'] = proj.id
        project_dict['provision_details'] = pd_list

        if include_request_flag:
            request_list = []
            project_dict['requests'] = request_list
            for crams_req in reqs:
                request_list.append(populate_request_data(crams_req))

    return Response(ret_dict)


class UserProjectListView(APIView):
    """
        class UserProjectListView
    """
    permission_classes = [IsAuthenticated]

    # noinspection PyUnusedLocal
    def get(self, request, format=None):
        """
            get
        :param request:
        :param format:
        :return:
        """
        return populate_user_project_list(request, False)


class UserProjectRequestListView(APIView):
    """
        UserProjectRequestListView
    """
    permission_classes = [IsAuthenticated]

    # noinspection PyUnusedLocal
    def get(self, request, format=None):
        """
            get
        :param request:
        :param format:
        :return:
        """
        return populate_user_project_list(request, True)


def populate_user_project_list(request, include_request_boolean):
    """
        populate_user_project_list
    :param request:
    :param include_request_boolean:
    :return:
    """
    project_objects = Project.objects.filter(
        project_contacts__contact__email=request.user.email,
        parent_project__isnull=True).order_by('title').distinct()
    ret_dict = {}
    ret_dict['user'] = UserSerializer(request.user).data

    project_list = []
    ret_dict['projects'] = project_list
    for project in project_objects:
        project_dict = {}
        project_list.append(project_dict)
        project_dict['title'] = project.title
        project_dict['id'] = project.id
        if include_request_boolean:
            request_list = []
            project_dict['requests'] = request_list
            for cramsRequest in project.requests.filter(
                    parent_request__isnull=True).order_by('end_date'):
                request_list.append(populate_request_data(cramsRequest))
    return Response(ret_dict)


def populate_request_data(crams_request):
    """
        populate_request_data
    :param crams_request:
    :return:
    """
    request_dict = {}
    request_dict['id'] = crams_request.id

    request_dict['status'] = crams_request.request_status.status
    request_dict['expiry'] = crams_request.end_date
    request_dict['funding'] = crams_request.funding_scheme.funding_scheme

    compute_list = []
    request_dict['compute_requests'] = compute_list
    for compute_request in crams_request.compute_requests.all():
        compute_data = ComputeRequestSerializer(compute_request).data
        compute_list.append(compute_data)
        # override id value to name value
        compute_data['compute_product'] = {
            'id': compute_request.compute_product.id,
            'name': compute_request.compute_product.name
        }

    storage_list = []
    request_dict['storage_requests'] = storage_list
    for storage_request in crams_request.storage_requests.all():
        storage_data = StorageRequestSerializer(storage_request).data
        storage_list.append(storage_data)
        # override id value to name value
        storage_data['storage_product'] = {
            'id': storage_request.storage_product.id,
            'name': storage_request.storage_product.name
        }

    return request_dict
