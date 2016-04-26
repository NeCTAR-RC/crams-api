import pprint
import json
from rest_framework import status
from account.models import User
from crams_api.views import ProjectViewSet, ApproveRequestViewSet
from crams_api.views import DeclineRequestViewSet, ProvisionProjectViewSet
from crams_api.views import UpdateProvisionProjectViewSet
from rest_framework.test import APITestCase, APIRequestFactory
from crams.models import Contact, CramsToken, Provider, ComputeProduct
from crams.models import StorageProduct
from crams.models import Request
from tests.testUtils import get_compute_requests_for_request
from tests.testUtils import get_storage_requests_for_request


__author__ = 'melvin luong, rafi m feroze'  # 'mmohamed'


class CRAMSApiTstCase(APITestCase):

    def setUp(self):
        self.pp = pprint.PrettyPrinter(indent=4)
        self.roleList = None
        testEmail = 'tests.merc@monash.edu'
        self.user = self._getUser('merctest', testEmail)
        self.contact, created = Contact.objects.get_or_create(
            title='Mr', given_name='Test', surname='MeRC', email=testEmail,
            phone='99020780', organisation='Monash University')
        self.token, created = CramsToken.objects.get_or_create(user=self.user)

        self.factory = APIRequestFactory()

    def _getUser(self, userName, testEmail):
        user, created = User.objects.get_or_create(
            username=userName, email=testEmail, password='merc2test')
        user.is_staff = True
        user.save()
        return user

    def _setUserRoles(self, roleList):
        self.token.ks_roles = json.dumps(roleList)
        self.token.save()
        # reload User to ensure latest permissions are available
        self.user = User.objects.get(pk=self.user.id)

    def _baseGetAPI(self, view, url, idStr=None):
        request = self.factory.get(url)
        request.user = self.user
        if idStr:
            return view(request, pk=idStr)
        return view(request)

    def _create_project_common(self, test_data):
        view = ProjectViewSet.as_view({'get': 'list', 'post': 'create'})
        request = self.factory.post(
            'api/project',
            test_data,
            HTTP_AUTHORIZATION='Token {}'.format(
                self.token.key))
        response = view(request)

        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED, response.data)
        self.assertIsNot(response.data.get("id"), 0, response.data)
        self.assertEqual(response.data.get("title"),
                         test_data["title"], response.data)

        return response

    def _get_project_data_by_id(self, project_id):
        view = ProjectViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get(
            'api/project',
            HTTP_AUTHORIZATION='Token {}'.format(
                self.token.key))
        response = view(request, pk=str(project_id))
        # Expecting HTTP 200 response status
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)
        return response

    def debugResponse(self, response, actStr):
        project = response.data
        self.assertIsNotNone(project, 'Project Data is null after ' + actStr)

        new_project_id = project.get("id", None)
        self.assertIsNotNone(
            new_project_id, 'Project Id is null after ' + actStr)

        requests = []
        inRequests = project.get('requests', None)
        if not inRequests:
            self.pp.pprint(response.data)
        self.assertIsNotNone(
            inRequests, 'No Requests returned after ' + actStr)
        for r in project.get('requests', None):
            print('Request ' + str(len(requests) + 1))
            print(r['id'], '/', r['project'],
                  r['request_status'], r['parent_request'])
            if r.get('parent_request', None):
                print('      - archived')

    def _update_project_common(
            self,
            test_data,
            old_request_id,
            instances,
            cores,
            quota,
            updateValidateFn=None):
        def _updateSuccessFn(response):
            # check HTTP 200
            self.assertEqual(response.status_code,
                             status.HTTP_200_OK, response.data)

            # check new project and requests is created with new id
            project = response.data
            self.assertIsNotNone(project, 'Project Data is null after update')

            new_project_id = project.get("id", None)
            self.assertIsNotNone(
                new_project_id, 'Project Id is null after update')
            self.assertNotEqual(
                new_project_id, test_data.get('id'), response.data)

            requests = []
            for r in project.get('requests', None):
                if not r.get(
                        'parent_request',
                        None):  # ignore archived requests
                    requests.append(r)

            self.assertIsNotNone(
                requests, 'No requests returned after project update')
            self.assertEqual(
                len(requests), 1,
                'Expected one request returned, got ' + str(len(requests)))
            for request in requests:
                new_request_id = request.get('id', None)
                self.assertIsNotNone(
                    new_request_id, 'Request Id is none after update')
                self.assertNotEqual(
                    new_request_id,
                    old_request_id,
                    'New Request id is same as old after update')
                # check requests has changed
                for cr in request.get('compute_requests', []):
                    if instances:
                        self.assertEqual(
                            cr["instances"], instances, response.data)
                    if cores:
                        self.assertEqual(cr["cores"], cores, response.data)
                for sr in request.get('storage_requests', []):
                    if quota:
                        self.assertEqual(sr["quota"], quota, response.data)

            return response

        view = ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update'})
        request = self.factory.put(
            'api/project',
            test_data,
            HTTP_AUTHORIZATION='Token {}'.format(
                self.token.key))
        request.user = self.user
        response = view(request, pk=test_data.get('id'))

        if updateValidateFn:
            return updateValidateFn(response)
        else:
            return _updateSuccessFn(response)


class AdminBaseTstCase(CRAMSApiTstCase):

    def setUp(self):
        CRAMSApiTstCase.setUp(self)
        approverRoles = ['nectar_approver', 'vicnode_approver']
        self._setUserRoles(approverRoles)

    def _assert_approve_request(self, projectId, approval_notes="",
                                expected_http_status=status.HTTP_200_OK,
                                expected_req_status="Approved",
                                expected_status_code="A"):
        # setup tests data
        req = Request.objects.get(project_id=projectId, parent_request=None)
        test_data = {
            "compute_requests": get_compute_requests_for_request(req),
            "storage_requests": get_storage_requests_for_request(req),
            "approval_notes": approval_notes
        }

        view = ApproveRequestViewSet.as_view(
            {'get': 'retrieve', 'put': 'update'})
        # Approve request where id == req.id
        request = self.factory.put('api/approve_request/', test_data)
        request.user = self.user
        response = view(request, pk=str(req.id))

        # Expected HTTP status
        self.assertEquals(response.status_code,
                          expected_http_status, response.data)
        if response.status_code == status.HTTP_200_OK:
            # The following are valid if approve is successful
            # Expecting request ID to change
            self.assertNotEqual(response.data.get('id'), req.id, response.data)
            # Expected Approve status
            self.assertEqual(response.data.get('request_status'),
                             expected_req_status, response.data)
            # Expected approval notes
            self.assertEqual(response.data.get(
                'approval_notes'), approval_notes, response.data)
            # Expected status code in the databse
            request_obj = Request.objects.get(pk=int(response.data.get('id')))
            self.assertEqual(request_obj.request_status.code,
                             expected_status_code, response.data)

        return response

    def _assert_decline_request(self, projectId, approval_notes="",
                                expected_http_status=status.HTTP_200_OK,
                                expected_req_status="Declined",
                                expected_status_code="D"):
        # setup tests data
        req = Request.objects.get(project_id=projectId, parent_request=None)
        test_data = {
            "compute_requests": get_compute_requests_for_request(req),
            "storage_requests": get_storage_requests_for_request(req),
            "approval_notes": approval_notes
        }

        view = DeclineRequestViewSet.as_view(
            {'get': 'retrieve', 'put': 'update'})
        # Approve request where id == req.id
        request = self.factory.put('api/decline_request/', test_data)
        request.user = self.user
        response = view(request, pk=str(req.id))

        # Expected HTTP status
        self.assertEquals(response.status_code,
                          expected_http_status, response.data)
        if response.status_code == status.HTTP_200_OK:
            # The following is valid if approve is successful
            # Expecting request ID to change
            self.assertNotEqual(response.data.get('id'), req.id, response.data)
            # Expected Approve status
            self.assertEqual(response.data.get('request_status'),
                             expected_req_status, response.data)
            # Expected approval notes
            self.assertEqual(response.data.get(
                'approval_notes'), approval_notes, response.data)
            # Expected status code in the databse
            request_obj = Request.objects.get(pk=int(response.data.get('id')))
            self.assertEqual(request_obj.request_status.code,
                             expected_status_code, response.data)

        return response


class ProvisionBaseTstCase(CRAMSApiTstCase):

    def setUp(self):
        CRAMSApiTstCase.setUp(self)

        # Setup Provisioner Role
        keystoneRoles = ['crams_provisioner']
        self._setUserRoles(keystoneRoles)

        # Make user provider for all products
        self.providers = {}
        for p in Provider.objects.all():
            self.providers[p.name] = p

    def setUserProviderFor(self, providerName):
        self.provider = Provider.objects.get(name=providerName)
        self.assertIsNotNone(
            self.provider, 'No provider found with name ' + providerName)

        self.provider.crams_user = self.user
        self.provider.active = True
        self.provider.save()

        # reload User to ensure latest provider role is available,
        # required for some DB like SQLite
        # self.user = User.objects.get(pk=self.user.id)

        for c in ComputeProduct.objects.all():
            c.provider = self.provider
            c.save()
        for s in StorageProduct.objects.all():
            s.provider = self.provider
            s.save()

    def _returnFetchProvisionListResponse(self):
        view = ProvisionProjectViewSet.as_view({'get': 'list'})
        url = 'api/provision_project/list/'
        return self._baseGetAPI(view, url)

    def _returnProvisionUpdateResponse(self, test_data):
        view = UpdateProvisionProjectViewSet.as_view(
            {'get': 'list', 'post': 'create'})
        request = self.factory.post('api/provision_project/update/', test_data)
        request.user = self.user

        return view(request)
