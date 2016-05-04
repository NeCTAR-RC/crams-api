import datetime

from api.v1.projectRequestListAPI import ApproverReviewerRequestListView
from api.v1.projectRequestListAPI import FundingBodyAllocationsCounter
from django.db.models import Q
from rest_framework import status

from crams.DBConstants import REQUEST_STATUS_SUBMITTED
from crams.DBConstants import REQUEST_STATUS_UPDATE_OR_EXTEND
from crams.models import FundingScheme
from crams.models import Project, RequestStatus, Request, FundingBody
from api.v1.tests.baseTest import AdminBaseTstCase
from api.v1.views import ApproveRequestViewSet

__author__ = 'melvin luong, rafi m feroze'  # 'mmohamed'


class ApproverReviewerRequestListTest(AdminBaseTstCase):

    def setUp(self):
        AdminBaseTstCase.setUp(self)

        self.funding_body = FundingBody.objects.get(name='NeCTAR')
        self.funding_scheme = FundingScheme.objects.get(
            funding_scheme='NeCTAR National Merit')

        self.project_1 = Project.objects.create(
            title='Test Project 1',
            description="Test Project 1",
            notes="Test Project 1",
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.project_2 = Project.objects.create(
            title='Test Project 2',
            description="Test Project 2",
            notes="Test Project 2",
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.project_3 = Project.objects.create(
            title='Test Project 3',
            description="Test Project 3",
            notes="Test Project 3",
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.project_4 = Project.objects.create(
            title='Test Project 4',
            description="Test Project 4",
            notes="Test Project 4",
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.project_6 = Project.objects.create(
            title='Test Project 6',
            description="Test Project 6",
            notes="Test Project 6",
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.project_5 = Project.objects.create(
            title='Test Project 5',
            parent_project=self.project_6,
            description="Test Project 5",
            notes="Test Project 5",
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)

        self.project_7 = Project.objects.create(
            title='Test Project 7',
            description="Test Project 7",
            notes="Test Project 7",
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.project_8 = Project.objects.create(
            title='Test Project 8',
            description="Test Project 8",
            notes="Test Project 8",
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.project_9 = Project.objects.create(
            title='Test Project 9',
            description="Test Project 9",
            notes="Test Project 9",
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)

        self.request_status_x = RequestStatus.objects.get(
            code='X', status='Update/Extension Requested')
        self.request_status_e = RequestStatus.objects.get(
            code='E', status='Submitted')
        self.request_status_n = RequestStatus.objects.get(
            code='N', status='New')
        self.request_status_l = RequestStatus.objects.get(
            code='L', status='Legacy Submission')
        self.request_status_a = RequestStatus.objects.get(
            code='A', status='Approved')
        self.request_status_p = RequestStatus.objects.get(
            code='P', status='Provisioned')

        self.request_1 = Request.objects.create(
            project=self.project_1,
            request_status=self.request_status_x,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date.today(),
            end_date=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.request_2 = Request.objects.create(
            project=self.project_2,
            request_status=self.request_status_e,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date.today(),
            end_date=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.request_3 = Request.objects.create(
            project=self.project_3,
            request_status=self.request_status_n,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date.today(),
            end_date=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.request_4 = Request.objects.create(
            project=self.project_4,
            request_status=self.request_status_l,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date.today(),
            end_date=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)

        self.request_6 = Request.objects.create(
            project=self.project_6,
            request_status=self.request_status_x,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date.today(),
            end_date=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)

        self.request_5 = Request.objects.create(
            project=self.project_5,
            parent_request=self.request_6,
            request_status=self.request_status_a,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date.today(),
            end_date=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)

        self.request_7 = Request.objects.create(
            project=self.project_7,
            request_status=self.request_status_a,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date.today(),
            end_date=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)

        self.request_8 = Request.objects.create(
            project=self.project_8,
            request_status=self.request_status_p,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date(
                2015,
                1,
                20),
            end_date=datetime.date(
                2015,
                12,
                20),
            created_by=self.user,
            updated_by=self.user)

        self.request_9 = Request.objects.create(
            project=self.project_9,
            request_status=self.request_status_p,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date(
                2015,
                7,
                20),
            end_date=datetime.date(
                9999,
                10,
                20),
            created_by=self.user,
            updated_by=self.user)

    # Test Rest GET for Approver Reviewer Request only returns request status
    # 'X', 'E' & 'N'
    def test_approver_reviewer_request_view(self):
        view = ApproverReviewerRequestListView.as_view()
        request = self.factory.get('api/approve_list')
        request.user = self.user
        response = view(request)

        # Expecting HTTP 200
        self.assertEquals(response.status_code,
                          status.HTTP_200_OK, response.data)
        # Expecting 3 results from response
        self.assertEquals(len(response.data['projects']), 3, response.data)
        # Expected results of response status code 'X'
        self.assertEquals(response.data['projects'][0]['requests'][0][
                          'status'], "Update/Extension Requested",
                          response.data)
        # Expected results of response status code 'E'
        self.assertEquals(response.data['projects'][1]['requests'][
                          0]['status'], "Submitted", response.data)
        # Expected results of response status code 'X'
        self.assertEquals(response.data['projects'][2]['requests'][0][
                          'status'], "Update/Extension Requested",
                          response.data)

    # tests list of approved allocations for fundingbody - status 'A'
    def test_approved_allocations_for_funding_body(self):
        view = ApproverReviewerRequestListView.as_view()
        request = self.factory.get('api/approve_list/?req_status=Approved')
        request.user = self.user
        response = view(request)

        # Expecting HTTP 200
        self.assertEquals(response.status_code,
                          status.HTTP_200_OK, response.data)
        # Expecting 3 results from response
        self.assertEquals(len(response.data['projects']), 1)
        # Expected results of response status code 'A'
        self.assertEquals(response.data['projects'][0]['requests'][
                          0]['status'], "Approved", response.data)

    def test_allocation_counter(self):
        view = FundingBodyAllocationsCounter.as_view()
        request = self.factory.get('api/alloc_counter')
        request.user = self.user
        response = view(request)

        # Expecting HTTP 200
        self.assertEquals(response.status_code,
                          status.HTTP_200_OK, response.data)
        # expecting 2 approved, 1 active and 1 expired
        self.assertEquals(response.data['counter'][
                          'approved'], 1, response.data)
        self.assertEquals(response.data['counter']['active'], 1, response.data)
        self.assertEquals(response.data['counter'][
                          'expired'], 1, response.data)


class ApproveRequestViewSetTest(AdminBaseTstCase):
    fixtures = ['v1/test_common_data', 'v1/test_nectar_data']

    def setUp(self):
        AdminBaseTstCase.setUp(self)

    # tests get list of projects from fixtures
    def test_approve_get_request(self):
        view = ApproveRequestViewSet.as_view({'get': 'list'})
        request = self.factory.get('api/approve_request')
        request.user = self.user
        response = view(request)

        # HTTP 200
        self.assertEquals(response.status_code,
                          status.HTTP_200_OK, response.data)
        # get submitted and update/extend requests
        projects = Project.objects.filter(
            Q(requests__request_status__code="E") |
            Q(requests__request_status__code="X"))
        self.assertEquals(len(response.data), len(projects), response.data)

    # def test_approve_get_request_without_authorization(self):
    #     keystoneRoles = ['not_crams_provisioner']
    #     self._setUserRoles(keystoneRoles)
    #     view = ApproveRequestViewSet.as_view({'get': 'list'})
    #     request = self.factory.get('api/approve_request')
    #     request.user = self.user
    #     response = view(request)
    #
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # testing change of request status from 'E - Submitted' to 'A - Approved'
    def test_approve_submitted_request(self):
        # setup test_data
        # .get(title="Test Project 2 - E: Submitted")
        projList = Project.objects.filter(
            requests__request_status__code=REQUEST_STATUS_SUBMITTED)
        if projList.exists():
            self._assert_approve_request(
                projList[0].id, approval_notes="Approve request for project 2")

    # testing change request status from 'X - Update/Extension Requested' to
    # 'A - Approved'
    def test_approve_update_extend_request(self):
        # setup test_data
        projList = Project.objects.filter(
            requests__request_status__code=REQUEST_STATUS_UPDATE_OR_EXTEND)
        # proj = Project.objects.get(title="Test Project 5 - X:
        # Update/Extension Request")
        self._assert_approve_request(
            projList[0].id, approval_notes="Approve request for project 5")

    # Disabled for now, current view does not handle legacy submission
    # testing change request status from 'L - Legacy Submission' to 'M -
    # Legacy Approved'
    def _test_approve_legacy_submission_request(self):
        # setup test_data
        proj = Project.objects.get(
            title="Test Project 8 - L: Legacy Submission")
        self._assert_approve_request(
            proj.id,
            approval_notes="Approve request for project 8",
            expected_req_status="Legacy Approved",
            expected_status_code="M")
