from rest_framework import status

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from crams.api.v1.tests import baseCramsFlow
from tests.sampleData import get_base_nectar_project_data
from crams.api.v1 import views as v1_views


class DeleteTest(baseCramsFlow.BaseCramsFlow):

    def setUp(self):
        baseCramsFlow.BaseCramsFlow.setUp(self)
        self.test_data = get_base_nectar_project_data(self.user.id,
                                                      self.contact)
        self.testCount = self.CREATE_NEW_PROJECT
        self.response = self.flowUpTo(self.testCount)

    # Test Rest Delete fail for Project
    def test_project_delete_fail(self):
        view = v1_views.ProjectViewSet.as_view({'get': 'list'})
        # Using the standard RequestFactory API to create a form POST request
        factory = APIRequestFactory()
        request = factory.delete('/api/v1/project/')
        force_authenticate(request, user=self.user)

        project = self.response.data
        response = view(request, pk=project.get('id'))

        # HTTP 405
        self.assertEquals(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            response.data)

    # Test Rest Delete fail for Request
    def test_request_delete_fail(self):
        view = v1_views.RequestViewSet.as_view({'get': 'list'})
        # Using the standard RequestFactory API to create a form POST request
        factory = APIRequestFactory()
        request = factory.delete('/api/v1/request/')
        force_authenticate(request, user=self.user)

        requests = self.response.data.get('requests')
        response = view(request, pk=requests[0].get('id'))

        # HTTP 405
        self.assertEquals(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            response.data)

    # Test Rest Delete fail for Contact
    def test_contact_delete_fail(self):
        view = v1_views.ContactViewSet.as_view({'get': 'list'})
        # Using the standard RequestFactory API to create a form POST request
        factory = APIRequestFactory()
        request = factory.delete('/api/v1/contact/')
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.contact.id)

        # HTTP 405
        self.assertEquals(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            response.data)
