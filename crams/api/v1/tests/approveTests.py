import datetime

from crams.api.v1.projectRequestListAPI import ApproverReviewerRequestListView
from crams.api.v1.projectRequestListAPI import FundingBodyAllocationsCounter
from rest_framework import status

from crams import DBConstants
from crams.models import FundingScheme
from crams.models import Project, RequestStatus, Request, FundingBody
from crams.models import ProjectContact, ContactRole
from crams.api.v1.tests.baseTest import AdminBaseTstCase
from crams.api.v1.views import ApproveRequestViewSet


def get_request_status_map():
    ret_map = dict()
    for rs in RequestStatus.objects.all():
        ret_map[rs.code] = {
            'code': rs.code,
            'status': rs.status
        }
    return ret_map


class ApproverReviewerRequestListTest(AdminBaseTstCase):

    def setUp(self):
        AdminBaseTstCase.setUp(self)

        self.funding_body = FundingBody.objects.get(name='NeCTAR')
        self.funding_scheme = FundingScheme.objects.get(
            funding_scheme='NeCTAR National Merit')
        self.request_status_map = get_request_status_map()

        role_obj = ContactRole.objects.get(name=DBConstants.APPLICANT)

        def setup_project(title_str, parent_project=None):
            proj = Project.objects.create(
                title=title_str,
                description=title_str + " : Desc",
                notes=title_str + " : notes",
                creation_ts=datetime.date.today(),
                last_modified_ts=datetime.date.today(),
                created_by=self.user,
                updated_by=self.user,
                parent_project=parent_project
            )
            ProjectContact.objects.create(
                project=proj, contact=self.project_contact,
                contact_role=role_obj)
            return proj

        self.project_1 = setup_project('Test Project 1')
        self.project_2 = setup_project('Test Project 2')
        self.project_3 = setup_project('Test Project 3')
        self.project_4 = setup_project('Test Project 4')
        self.project_6 = setup_project('Test Project 6')
        self.project_5 = setup_project(
            'Test Project 5', parent_project=self.project_6)
        self.project_7 = setup_project('Test Project 7')
        self.project_8 = setup_project('Test Project 8')
        self.project_9 = setup_project('Test Project 9')

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
        expected_status = self.request_status_map.get('X')
        self.assertEquals(response.data['projects'][0]['requests'][0][
                          'status'], expected_status, response.data)
        # Expected results of response status code 'E'
        expected_status = self.request_status_map.get('E')
        self.assertEquals(response.data['projects'][1]['requests'][
                          0]['status'], expected_status, response.data)
        # Expected results of response status code 'X'
        expected_status = self.request_status_map.get('X')
        self.assertEquals(response.data['projects'][2]['requests'][0][
                          'status'], expected_status,
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
        expected_status = self.request_status_map.get('A')
        self.assertEquals(response.data['projects'][0]['requests'][
                          0]['status'], expected_status, response.data)

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

    # Test Approvers have edit Access to Request
    def test_approver_edit_access(self):
        def update_success_fn(response):
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                             'Approver should have edit access : {}'.format(
                                 repr(response.data)))
        view = ApproverReviewerRequestListView.as_view()
        request = self.factory.get('api/approve_list')
        request.user = self.user
        response = view(request)

        # HTTP 200
        self.assertEquals(
            response.status_code, status.HTTP_200_OK, response.data)
        for proj in response.data.get("projects"):
            response = self._get_project_data_by_id(proj.get("id"))
            request1 = response.data.get("requests")[0]
            instances = 4
            cores = 4
            quota = 4000
            self._update_project_common(response.data, request1.get("id"),
                                        instances, cores, quota,
                                        updateValidateFn=update_success_fn)


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

        # HTTP 405
        self.assertEquals(response.status_code,
                          status.HTTP_405_METHOD_NOT_ALLOWED, response.data)

    def fetch_submitted_projects(self):
        proj_list = Project.objects.filter(
            requests__request_status__code=DBConstants.REQUEST_STATUS_SUBMITTED
        )
        self.assertTrue(proj_list.exists(),
                        'Approve test requires Submitted Projects')
        return proj_list

    def test_approve_with_invalid_national_percent(self):
        def anon_fn(national_percent, allocation_node_is_none=False):
            proj_list = self.fetch_submitted_projects()
            allocation_node = None
            if not allocation_node_is_none:
                allocation_node = DBConstants.ALLOCATION_HOME_MONASH
            self._assert_approve_request(
                proj_list[0].id,
                national_percent=national_percent,
                approval_notes="Approve request with invalid national percent",
                expected_http_status=status.HTTP_400_BAD_REQUEST,
                expected_req_status=None,
                expected_status_code=None,
                allocation_node=allocation_node)
        # National Percent not given
        anon_fn(None)
        # National Percent < 0
        anon_fn(-4)
        # National Percent > 100
        anon_fn(102)
        # National Percent non-integer
        anon_fn(66.345)
        # National Percent is 100, allocation_node is given
        anon_fn(100)
        # National Percent is valid, less than 100, but no allocation_node
        anon_fn(45, allocation_node_is_none=True)

    def test_approve_with_valid_national_percent(self):
        proj_list = self.fetch_submitted_projects()
        self._assert_approve_request(
            proj_list[0].id,
            national_percent=35,
            allocation_node=DBConstants.ALLOCATION_HOME_MONASH,
            approval_notes="Approve request with valid national percent")

    # testing change of request status from 'E - Submitted' to 'A - Approved'
    def test_approve_submitted_request(self):
        # setup test_data
        # .get(title="Test Project 2 - E: Submitted")
        proj_list = self.fetch_submitted_projects()
        self._assert_approve_request(
            proj_list[0].id,
            national_percent=100,
            approval_notes="Approve request for project 2")

    # testing change request status from 'X - Update/Extension Requested' to
    # 'A - Approved'
    def test_approve_update_extend_request(self):
        # setup test_data
        status = DBConstants.REQUEST_STATUS_UPDATE_OR_EXTEND
        projList = Project.objects.filter(
            requests__request_status__code=status)
        # proj = Project.objects.get(title="Test Project 5 - X:
        # Update/Extension Request")
        self._assert_approve_request(
            projList[0].id,
            national_percent=100,
            approval_notes="Approve request for project 5")

    # Disabled for now, current view does not handle legacy submission
    # testing change request status from 'L - Legacy Submission' to 'M -
    # Legacy Approved'
    def _test_approve_legacy_submission_request(self):
        # setup test_data
        proj = Project.objects.get(
            title="Test Project 8 - L: Legacy Submission")
        self._assert_approve_request(
            proj.id,
            national_percent=100,
            approval_notes="Approve request for project 8",
            expected_req_status="Legacy Approved",
            expected_status_code="M")

# AssertionError: 400 != 200 : {'allocation_node': ['This field is required.']}
