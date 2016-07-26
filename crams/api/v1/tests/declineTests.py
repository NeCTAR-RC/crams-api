import datetime

from django.db.models import Q
from rest_framework import status

from crams.models import FundingBody, FundingScheme, Project, RequestStatus
from crams.models import Request
from crams.api.v1.tests.baseTest import AdminBaseTstCase
from crams.api.v1.views import DeclineRequestViewSet

__author__ = 'melvin luong, rafi m feroze'


class DeclineRequestViewSetTest(AdminBaseTstCase):

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

        self.request_status_x = RequestStatus.objects.get(
            code='X', status='Update/Extension Requested')
        self.request_status_e = RequestStatus.objects.get(
            code='E', status='Submitted')
        self.request_status_l = RequestStatus.objects.get(
            code='L', status='Legacy Submission')

        self.request_1 = Request.objects.create(
            project=self.project_1,
            request_status=self.request_status_e,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date.today(),
            end_date=datetime.date.today(),
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.request_2 = Request.objects.create(
            project=self.project_2,
            request_status=self.request_status_x,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date.today(),
            end_date=datetime.date.today(),
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.request_3 = Request.objects.create(
            project=self.project_3,
            request_status=self.request_status_l,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date.today(),
            end_date=datetime.date.today(),
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)

    # gets all current request
    def test_decline_request_get(self):
        view = DeclineRequestViewSet.as_view({'get': 'list'})
        request = self.factory.get('api/decline_request')
        request.user = self.user
        response = view(request)

        # HTTP 200
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)
        # Expecting 2 results from response
        # get submitted and update/extend requests
        projects = Project.objects.filter(
            Q(requests__request_status__code="E") |
            Q(requests__request_status__code="X"))
        self.assertEqual(len(response.data), len(projects))
        self.assertEqual(response.data[0]['project'][
                         'title'], 'Test Project 1', response.data)
        self.assertEqual(response.data[1]['project'][
                         'title'], 'Test Project 2', response.data)

    # testing change of request status from 'E - Submitted' to 'R - Declined'
    def test_decline_submitted_request(self):
        test_data = {
            'approval_notes': 'Declining request where status code was E'}

        view = DeclineRequestViewSet.as_view(
            {'get': 'retrieve', 'put': 'update'})
        # Decline request where id == 1 with test_data
        request = self.factory.put('api/decline_request', test_data)
        request.user = self.user
        response = view(request, pk=self.request_1.id)

        # HTTP 200
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)
        # expecting new request id
        self.assertNotEqual(response.data.get(
            "id"), self.request_1.id, response.data)
        # check status has been changed to declined
        self.assertEqual(response.data.get('request_status'),
                         "Declined", response.data)
        # check approval notes
        self.assertEqual(response.data.get('approval_notes'),
                         test_data['approval_notes'], response.data)
        # check the database for status code == 'R'
        request_obj = Request.objects.get(pk=int(response.data.get('id')))
        self.assertEqual(request_obj.request_status.code, 'R', response.data)

    # testing change of request status from 'X - Updated/Extension Requested'
    # to 'J - Updated/Extension Declined'
    def test_decline_update_extend_request(self):
        test_data = {
            'approval_notes': 'Declining request where status code was X'}

        view = DeclineRequestViewSet.as_view(
            {'get': 'retrieve', 'put': 'update'})
        # Decline request where id == 2 with test_data
        request = self.factory.put('api/decline_request', test_data)
        request.user = self.user
        response = view(request, pk=self.request_2.id)

        # HTTP 200
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)
        # expecting new request id
        self.assertNotEqual(response.data.get(
            'id'), self.request_2.id, response.data)
        # check status has been changed to declined
        self.assertEqual(response.data.get('request_status'),
                         "Update/Extension Declined", response.data)
        # check approval notes
        self.assertEqual(response.data.get('approval_notes'),
                         test_data['approval_notes'], response.data)
        # check the database for status code == 'J'
        request_obj = Request.objects.get(pk=int(response.data.get('id')))
        self.assertEqual(request_obj.request_status.code, 'J', response.data)

    # Disabled for now, current view does not handle legacy submission
    # testing change of request status from 'L - Legacy Submission' to 'O -
    # Updated/Extension Declined'
    def _test_decline_legacy_request(self):
        test_data = {
            'approval_notes': 'Declining request where status code was L'}

        view = DeclineRequestViewSet.as_view(
            {'get': 'retrieve', 'put': 'update'})
        # Decline request where id == 3
        request = self.factory.put('api/decline_request/3', test_data)
        request.user = self.user
        response = view(request, pk="3")

        # HTTP 200
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)
        # expecting new request id
        self.assertNotEqual(response.data.get('id'), 3, response.data)
        # check status has been changed to declined
        self.assertEqual(response.data.get('request_status'),
                         'Legacy Rejected', response.data)
        # check approval notes
        self.assertEqual(response.data.get('approval_notes'),
                         test_data['approval_notes'], response.data)
        # check the database for status code == 'O'
        request_obj = Request.objects.get(pk=int(response.data.get('id')))
        self.assertEqual(request_obj.request_status.code, 'O', response.data)

    # tests declining a 'R - rejected' request
    def test_decline_r(self):
        self.project = Project.objects.create(
            title='Test Project',
            description="Test Project",
            notes="Test Project",
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.request_status = RequestStatus.objects.get(
            code='R', status='Declined')
        self.request = Request.objects.create(
            project=self.project,
            request_status=self.request_status,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date.today(),
            end_date=datetime.date.today(),
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)

        test_data = {
            'approval_notes': 'Declining request where status code was R'}

        view = DeclineRequestViewSet.as_view(
            {'get': 'retrieve', 'put': 'update'})
        # Decline request where id == 4
        request = self.factory.put('api/decline_request/4', test_data)
        request.user = self.user
        response = view(request, pk="4")

        # HTTP 404
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND, response.data)
        # Expected error message
        self.assertEqual(response.data.get('detail'),
                         'Not found.', response.data)

    # tests declining a 'J - rejected' request
    def test_decline_j(self):
        self.project = Project.objects.create(
            title='Test Project',
            description="Test Project",
            notes="Test Project",
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.request_status = RequestStatus.objects.get(
            code='J', status='Update/Extension Declined')
        self.request = Request.objects.create(
            project=self.project,
            request_status=self.request_status,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date.today(),
            end_date=datetime.date.today(),
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)

        test_data = {
            'approval_notes': 'Declining request where status code was J'}

        view = DeclineRequestViewSet.as_view(
            {'get': 'retrieve', 'put': 'update'})
        # Decline request where id == 4
        request = self.factory.put('api/decline_request/4', test_data)
        request.user = self.user
        response = view(request, pk="4")

        # HTTP 404
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND, response.data)
        # Expected error message
        self.assertEqual(response.data.get('detail'),
                         'Not found.', response.data)

    # tests declining a 'O - rejected' request
    def test_decline_o(self):
        self.project = Project.objects.create(
            title='Test Project',
            description="Test Project",
            notes="Test Project",
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)
        self.request_status = RequestStatus.objects.get(
            code='O', status='Legacy Rejected')
        self.request = Request.objects.create(
            project=self.project,
            request_status=self.request_status,
            funding_scheme=self.funding_scheme,
            start_date=datetime.date.today(),
            end_date=datetime.date.today(),
            creation_ts=datetime.date.today(),
            last_modified_ts=datetime.date.today(),
            created_by=self.user,
            updated_by=self.user)

        test_data = {
            'approval_notes': 'Declining request where status code was O'}

        view = DeclineRequestViewSet.as_view(
            {'get': 'retrieve', 'put': 'update'})
        # Decline request where id == 4
        request = self.factory.put('api/decline_request/4', test_data)
        request.user = self.user
        response = view(request, pk="4")

        # HTTP 404
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND, response.data)
        # Expected error message
        self.assertEqual(response.data.get('detail'),
                         'Not found.', response.data)
