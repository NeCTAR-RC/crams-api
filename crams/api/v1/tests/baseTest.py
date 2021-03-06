import pprint

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from crams.tests import testUtils

from crams import roleUtils
from crams.account.models import User
from crams.api.v1 import utils as api_utils
from crams.api.v1 import views
from crams.models import Contact, CramsToken, Provider, ComputeProduct
from crams.models import Request, Project, ProjectContact, ContactRole
from crams.models import StorageProduct
from crams.tests import settings as test_settings


class CRAMSApiTstCase(APITestCase):

    def setUp(self):
        super(CRAMSApiTstCase, self).setUp()
        self.pp = pprint.PrettyPrinter(indent=4)
        self.roleList = None
        self.factory = APIRequestFactory()
        self.setup_new_user()

    def setup_new_user(self):
        username = api_utils.get_random_string(12)
        self.user = self.get_new_user(username, username + '@crams.tst')
        self.token, created = CramsToken.objects.get_or_create(user=self.user)
        self.user_contact, created = Contact.objects.get_or_create(
            title='Mr', given_name='Test', surname='MeRC',
            email=self.user.email, phone='99020780',
            organisation='Monash University')

    @classmethod
    def get_new_user(cls, username, testEmail):
        user, created = User.objects.get_or_create(
            username=username, email=testEmail, password=username)
        user.is_staff = True
        user.save()
        return user

    def set_user_roles(self, roleList):
        roleUtils.setup_case_insensitive_roles(self.user, roleList)
        # reload User to ensure latest permissions are available
        self.user = User.objects.get(pk=self.user.id)

    def apply_fn_to_userrole_combo(self, userrole_list, fn):
        for user_roles in api_utils.power_set_generator(userrole_list):
            if len(user_roles) > 0:
                self.set_user_roles(user_roles)
                fn()

    def _baseGetAPI(self, view, url, idStr=None):
        request = self.factory.get(url)
        request.user = self.user
        if idStr:
            return view(request, pk=idStr)
        return view(request)

    def base_put_api(self, view, url, put_data, id_str=None):
        request = self.factory.put(url, put_data)
        request.user = self.user
        if id_str:
            return view(request, pk=id_str)
        return view(request)

    def _create_project_common(self, test_data, validate_response=True):
        view = views.ProjectViewSet.as_view({'get': 'list', 'post': 'create'})
        request = self.factory.post('api/project', test_data)
        request.user = self.user
        response = view(request)
        if validate_response:
            self.assertEqual(response.status_code,
                             status.HTTP_201_CREATED, response.data)
            self.assertIsNot(response.data.get("id"), 0, response.data)
            self.assertEqual(response.data.get("title"),
                             test_data["title"], response.data)

        return response

    def _get_project_data_by_id(self, project_id, validate_response=True):
        view = views.ProjectViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get('api/project')
        request.user = self.user
        response = view(request, pk=str(project_id))
        if validate_response:
            # Expecting HTTP 200 response status
            self.assertEqual(response.status_code,
                             status.HTTP_200_OK, response.data)
        return response

    def add_project_contact_curr_user(self, project_id):
        # setup user as a contact, so that read/update can be done on Project
        # by current user
        project = Project.objects.get(pk=project_id)
        contact, created = Contact.objects.get_or_create(
            title='title', given_name=self.user.first_name,
            surname=self.user.last_name, email=self.user.email, phone='0',
            organisation='org')
        contact_role = ContactRole.objects.filter()[0]
        ProjectContact.objects.create(
            project=project, contact=contact, contact_role=contact_role)

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
                print('      - historic')

    def validate_requests_are_historic_on_project_update(
            self, pre_update_project_obj, new_project_id):

            prev_requests_qs = pre_update_project_obj.requests
            pre_update_req_count = prev_requests_qs.count()
            if not prev_requests_qs:
                return
            try:
                project_id = pre_update_project_obj.id
                post_update_project = Project.objects.get(pk=project_id)
                self.assertIsNotNone(
                    post_update_project.parent_project,
                    'Project not historic on update'
                )
                new_parent_project = post_update_project.parent_project
                self.assertEqual(
                    new_parent_project.id, new_project_id,
                    'Historic project id is not correct. Expected ' +
                    'parent_project {}, got {}'.format(new_project_id,
                                                       new_parent_project.id))
                post_update_non_historic_requests = \
                    post_update_project.requests.filter(
                        parent_request__isnull=True)
                self.assertFalse(
                    post_update_non_historic_requests.exists(),
                    'All requests must be historic for given project on update'
                )

                post_requests_qs = post_update_project.requests
                post_update_req_count = post_requests_qs.count()
                self.assertEqual(
                    pre_update_req_count, post_update_req_count,
                    'Request count mismatch pre-update {}, post update {}'.
                    format(pre_update_req_count, post_update_req_count))

                for request in post_requests_qs.all():
                    self.assertIsNotNone(
                        request.parent_request,
                        'Request not historic on update proj/req : {}/{}'.
                        format(post_update_project.id, request.id))

                    new_project_linked = request.parent_request.project.id
                    self.assertEqual(
                        new_project_linked, new_project_id,
                        'Historic request id {} not connected to correct '
                        'parent project, expected {} got {}'.format(
                            request.id, new_project_id, new_project_linked))

            except Project.DoesNotExist:
                self.assertTrue(False, 'old project is missing on update')

    def _update_project_common(
            self,
            test_data,
            old_request_id,
            instances,
            cores,
            quota,
            updateValidateFn=None):

        def _updateSuccessFn(response, pre_update_proj_obj):
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

            self.validate_requests_are_historic_on_project_update(
                pre_update_proj_obj, new_project_id)

            requests = []
            for r in project.get('requests', None):
                if not r.get(
                        'parent_request',
                        None):  # ignore historic requests
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

        view = views.ProjectViewSet.as_view(
            {'get': 'retrieve', 'put': 'update'})

        request = self.factory.put('api/project', test_data)
        request.user = self.user
        response = view(request, pk=test_data.get('id'))

        if updateValidateFn:
            return updateValidateFn(response)
        else:
            project_id = test_data.get('id')
            pre_update_proj_obj = Project.objects.get(pk=project_id)
            return _updateSuccessFn(response, pre_update_proj_obj)

    def validate_user_provision_details(self, provision_details_json):
        self.assertIsNotNone(provision_details_json,
                             'Expected Provision details, got none')

        message = provision_details_json.get('message')
        self.assertIsNone(message, 'User provision message not null: ' +
                          str(message))
        self.assertEqual(provision_details_json["status"], 'S',
                         'User provision status not sent')

    def validate_admin_provision_details(self, provision_details_json):
        self.assertIsNotNone(provision_details_json,
                             'Expected Provision details, got none')

        message = provision_details_json.get('message')
        self.assertIsNotNone(message,
                             'Admin provision message can not be null')
        self.assertEqual(provision_details_json["status"], 'F',
                         'Admin provision status must be Fail')


class AdminBaseTstCase(CRAMSApiTstCase):

    def setUp(self):
        CRAMSApiTstCase.setUp(self)
        self.project_contact = self.user_contact
        self.project_user = self.user
        self.setup_new_user()  # create approver user
        approver_roles = list(roleUtils.ROLE_FB_MAP.keys())
        self.set_user_roles(approver_roles)

    def _assert_approve_request(self, project_id, national_percent,
                                allocation_home=None,
                                approval_notes="",
                                expected_http_status=status.HTTP_200_OK,
                                expected_req_status="Approved",
                                expected_status_code="A"):
        # setup tests data
        req = Request.objects.get(project_id=project_id, parent_request=None)

        test_data = {
            "compute_requests":
                testUtils.get_compute_requests_for_request(req),
            "storage_requests":
                testUtils.get_storage_requests_for_request(req),
            "approval_notes": approval_notes,
            "national_percent": national_percent
        }
        if allocation_home:
            test_data["allocation_home"] = allocation_home

        view = views.ApproveRequestViewSet.as_view(
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
                                national_percent=None,
                                expected_status_code="D"):
        # setup tests data
        req = Request.objects.get(project_id=projectId, parent_request=None)
        test_data = {
            "compute_requests":
                testUtils.get_compute_requests_for_request(req),
            "storage_requests":
                testUtils.get_storage_requests_for_request(req),
            "approval_notes": approval_notes,
            "national_percent": 67,
            "allocation_home": test_settings.ALLOCATION_HOME_MONASH
        }

        view = views.DeclineRequestViewSet.as_view(
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
        self.set_user_roles(keystoneRoles)

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
        view = views.ProvisionProjectViewSet.as_view({'get': 'list'})
        url = 'api/provision_project/list/'
        return self._baseGetAPI(view, url)

    def _returnProvisionUpdateResponse(self, test_data):
        view = views.UpdateProvisionProjectViewSet.as_view(
            {'get': 'list', 'post': 'create'})
        request = self.factory.post('api/provision_project/update/', test_data)
        request.user = self.user

        return view(request)
