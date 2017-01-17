from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from crams.api.v1 import views as v1_views
from crams.api.v1.tests import baseCramsFlow
from crams.tests import sampleData


class PartialUpdateTest(baseCramsFlow.BaseCramsFlow):

    def setUp(self):
        baseCramsFlow.BaseCramsFlow.setUp(self)
        self.test_data = sampleData.get_base_nectar_project_data(
            self.user.id, self.user_contact)
        self.testCount = self.CREATE_NEW_PROJECT
        self.response = self.flowUpTo(self.testCount)

    # Test Rest partial update fail for Project
    def test_project_partial_update_fail(self):
        view = v1_views.ProjectViewSet.as_view({'get': 'retrieve',
                                                'patch': 'partial_update'})

        factory = APIRequestFactory()
        request = factory.patch('/api/v1/project/',
                                {"notes": "Test partial update fail"})
        force_authenticate(request, user=self.user)

        project = self.response.data
        response = view(request, pk=project.get('id'))

        # HTTP 405
        self.assertEquals(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            response.data)

    # Test Rest partial update fail for Request
    def test_request_partial_update_fail(self):
        view = v1_views.RequestViewSet.as_view({'get': 'retrieve',
                                                'patch': 'partial_update'})

        factory = APIRequestFactory()
        request = factory.patch('/api/v1/request/',
                                {"approval_notes": "Test partial update fail"})
        force_authenticate(request, user=self.user)

        requests = self.response.data.get('requests')
        response = view(request, pk=requests[0].get('id'))

        # HTTP 405
        self.assertEquals(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            response.data)

    # Test Rest partial update fail for  Contact
    def test_contact_partial_update_fail(self):
        view = v1_views.ContactViewSet.as_view({'get': 'retrieve',
                                                'patch': 'partial_update'})

        factory = APIRequestFactory()
        request = factory.patch('/api/v1/contact/',
                                {"email": "test.partial_fail@cart.test"})
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.user_contact.id)

        # HTTP 405
        self.assertEquals(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            response.data)
