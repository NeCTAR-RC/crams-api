from django.db.models import Q
from rest_framework import status

from crams.DBConstants import REQUEST_STATUS_PROVISIONED
from crams.models import ProjectContact, ProvisionDetails
from crams.models import Request, Project, Contact, ContactRole
from tests.sampleData import get_base_nectar_project_data
from crams.api.v1.tests.baseCramsFlow import BaseCramsFlow
from crams.api.v1.tests.baseTest import ProvisionBaseTstCase
from crams.api.v1.views import ProvisionProjectViewSet, ProvisionRequestViewSet
from crams.api.v1.views import UpdateProvisionProjectViewSet, ProjectViewSet


class ProvisionProjectViewSetTest(ProvisionBaseTstCase):
    fixtures = ['v1/test_common_data', 'v1/test_nectar_data']

    def setUp(self):
        ProvisionBaseTstCase.setUp(self)
        self.setUserProviderFor('NeCTAR')
        # override default user with fixture user

    # Test Rest Get list of projects for provisioning
    def test_request_list(self):
        # print('ProvisionProjectViewSetTest list')
        view = ProvisionProjectViewSet.as_view({'get': 'list'})
        request = self.factory.get('api/provision_project/list/')
        request.user = self.user
        response = view(request)

        # get the requests that have been approved
        # status should be Approved - A or Legacy Approved - M
        request_list = Request.objects.filter(
            Q(request_status__code="A") | Q(request_status__code="M"))

        # HTTP 200
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)
        # results should be 2 approved requests
        self.assertEqual(len(request_list), len(response.data), response.data)

    # Test Rest Get a project id
    def test_request_get(self):
        # print('ProvisionProjectViewSetTest get')
        view = ProvisionProjectViewSet.as_view({'get': 'list'})
        request = self.factory.get('api/provision_project/list/')
        request.user = self.user

        # get request where status is "Approved"
        # request_obj = Request.objects.get(request_status__code="A")

        response = view(request)  # , pk=request_obj.project.id)

        # HTTP 200
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)
        # check only Approved requests are provided
        for pData in response.data:
            for rData in pData["requests"]:
                requestStatus = rData['request_status']
                self.assertIsNotNone(requestStatus, 'Request Status is empty')
                self.assertEqual(
                    requestStatus,
                    'Approved',
                    'Returned requests with status other than Approved : ' +
                    requestStatus)
                self.assertIsNone(rData['parent_request'],
                                  'API returned archived requests')


class ProvisionRequestViewSetTest(ProvisionBaseTstCase):
    fixtures = ['v1/test_common_data', 'v1/test_nectar_data']

    def setUp(self):
        ProvisionBaseTstCase.setUp(self)
        self.setUserProviderFor('NeCTAR')
        # override default user with fixture user

    # Test Rest Get list of requests for provisioning
    def test_request_list(self):
        # print('ProvisionRequestViewSetTest list')
        view = ProvisionRequestViewSet.as_view({'get': 'list'})
        request = self.factory.get('api/provision_request/list/')
        request.user = self.user
        response = view(request)

        # get the requests that have been approved
        # status should be Approved - A or Legacy Approved - M
        request_list = Request.objects.filter(
            Q(request_status__code="A") | Q(request_status__code="M"))

        # HTTP 200
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)
        # results should be 2 approved requests
        self.assertEqual(len(request_list), len(response.data), response.data)

    # Test Rest Get a request id
    def test_request_get_without_authorization(self):
        keystoneRoles = ['not_crams_provisioner']
        self._setUserRoles(keystoneRoles)
        view = ProvisionRequestViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get('api/provision_request/list/')
        request.user = self.user

        # get request where status is "Approved"
        request_obj = Request.objects.get(request_status__code="A")

        response = view(request, pk=request_obj.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_request_get(self):
        # print('ProvisionRequestViewSetTest get')
        view = ProvisionRequestViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get('api/provision_request/list/')
        request.user = self.user

        # get request where status is "Approved"
        request_obj = Request.objects.get(request_status__code="A")

        response = view(request, pk=request_obj.id)

        # HTTP 200
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)
        # check project and request id's
        self.assertEqual(response.data["id"], request_obj.id, response.data)
        self.assertEqual(response.data["project"],
                         request_obj.project.id, response.data)


class UpdateProvisionViewSetTest(ProvisionBaseTstCase):
    fixtures = ['v1/test_common_data', 'v1/test_nectar_data']

    def setUp(self):
        ProvisionBaseTstCase.setUp(self)
        self.setUserProviderFor('NeCTAR')

    # Test Rest Get list of projects and its requests for provisioning
    def test_provision_get_list(self):
        response = self._returnFetchProvisionListResponse()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_provision_get_update_without_authorization(self):
        keystoneRoles = ['not_crams_provisioner']
        self._setUserRoles(keystoneRoles)
        # print('--- update sample ---')
        view = UpdateProvisionProjectViewSet.as_view({'get': 'list'})
        url = 'api/provision_project/update/'
        response = self._baseGetAPI(view, url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_provision_get_update(self):
        # print('--- update sample ---')
        view = UpdateProvisionProjectViewSet.as_view({'get': 'list'})
        url = 'api/provision_project/update/'
        response = self._baseGetAPI(view, url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _get_provision_test_data(self):
        # print('--- test_provision_update ---')
        test_data = {
            "id": 3,
            "message": "",
            "success": True,
            "requests": [{
                "id": 37,
                "storage_requests": [
                    {
                        "id": 25,
                        "message": "Sample request storage_request message ",
                        "success": True,
                        "storage_product": {
                            "id": -1,
                            "name": "NeCTAR Volume (Monash)"
                        }
                    }
                ],
                "compute_requests": [
                    {
                        "compute_product": {
                            "id": 1,
                            "name": "NeCTAR Compute"
                        },
                        "id": 37,
                        "message": "Sample request compute_request message ",
                        "success": True
                    }
                ]
            }],
            "project_ids": [
                {
                    "id": 230,
                    "identifier": "simon-tests-01",
                    "system": {
                        "id": 1,
                        "system": "NeCTAR"
                    }
                }
            ]
        }

        return test_data

    def _printRequests(self, rList):
        for sr in rList:
            p = sr.provision_details
            if p:
                print(sr.id, p.status, p.provider, p.message)

        # printRequests(req.compute_requests.all())
        # printRequests(req.storage_requests.all())

    def test_provision_rules(self):
        # List provision before updating, this allows for provision_details
        # value to be associated with Product Requests (compute and storage)
        response = self._returnFetchProvisionListResponse()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            'test_provision_rules - Failed to fetch provision_list, ' +
            'data: {}'.format(repr(response.data)))

        # update provisioning details
        test_data = self._get_provision_test_data()
        response = self._returnProvisionUpdateResponse(test_data)
        # check if update was successfull: HTTP 201
        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED, response.data)
        self._post_provision_static_fields(test_data["id"])

    # Issue 525 - As NeCTAR Core Services I want users to be stopped from
    # editing fields required to be static after approve action
    #  - fields cannot be modified include Project Identifier(all projects)
    #    and Project Description(Nectar only) fields
    def _post_provision_static_fields(self, projectId):
        # setup user as a contact, so that read/update can be done on Project
        # by current user
        project = Project.objects.get(pk=projectId)
        contact, created = Contact.objects.get_or_create(
            title='title', given_name=self.user.first_name,
            surname=self.user.last_name, email=self.user.email, phone='0',
            organisation='org')
        contact_role = ContactRole.objects.filter()[0]
        ProjectContact.objects.create(
            project=project, contact=contact, contact_role=contact_role)

        view = ProjectViewSet.as_view({'get': 'retrieve'})
        response = self._baseGetAPI(view, 'api/project/', str(projectId))
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)

        test_data = response.data
        # modify existing request
        test_data["title"] = "New title"
        test_data["description"] = "New title"

        # update the existing request
        view = ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update'})
        request = self.factory.put('api/project', test_data)
        request.user = self.user
        response = view(request, pk=str(projectId))

        # should get error
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST, response.data)


class NectarProjectProvisionTest(BaseCramsFlow):

    def setUp(self):
        BaseCramsFlow.setUp(self)
        self.test_data = get_base_nectar_project_data(self.user.id,
                                                      self.contact)
        self.provisioner_name = 'NeCTAR'

    def _get_nectar_db_id_data(self):
        return {
            "identifier": "90345",
            "system": {
                "id": 6,
                "system": "NeCTAR_DB_Id"
            }
        }

    def _get_nectar_created_by_data(self):
        return {
            "identifier": "7eea469ec8ff4f9bba3f46766323b388",
            "system": {
                "id": 5,
                "system": "NeCTAR_Created_By"
            }
        }

    def _get_nectar_uuid_data(self):
        return {
            "identifier": "dfgh563477515b4dsdsda0618d21a6228e50",
            "system": {
                "id": 4,
                "system": "NeCTAR_UUID"
            }
        }

    def _fetch_project_ids_provisioned_for_system(
            self, project_id, system_name):
        project = Project.objects.get(pk=project_id)
        if hasattr(project, 'project_ids'):
            return project.project_ids.filter(system__system=system_name)

        return None

    def _preProvisionSetup(self, system_name):
        testCount = self.SUBMITTED_TO_APPROVE_RETURN_PROJECT
        response = self.flowUpTo(testCount)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, 'Project Approval fail')
        self._verify_project_provisioning_details(
            response,
            expected_provision_status=None,
            project_sent_for_provisioning_flag=False)

        project_id_qs = self._fetch_project_ids_provisioned_for_system(
            response.data.get('id'), system_name)
        if project_id_qs:
            self.assertFalse(
                project_id_qs.exists(),
                system_name +
                ' exists: Cannot test project provisioning.')

        return response

    def test_provision_NeCTAR_UUID_success(self):
        system_name = 'NeCTAR_UUID'
        response = self._preProvisionSetup(system_name)

        project_ids = response.data.get('project_ids', [])
        system_data_to_add = self._get_nectar_uuid_data()
        project_ids.append(system_data_to_add)
        provision_response, proj_data_response = \
            self.provisionGivenProjectResponse(self.provisioner_name,
                                               response,
                                               getProjectDataFlag=True,
                                               debug=False)

        self._checkProjectRequestStatusCode(
            proj_data_response, REQUEST_STATUS_PROVISIONED)
        self._verify_project_provisioning_details(
            proj_data_response,
            expected_provision_status=ProvisionDetails.PROVISIONED,
            project_sent_for_provisioning_flag=True)

        project_id = response.data.get('id', None)
        project_id_qs = self._fetch_project_ids_provisioned_for_system(
            project_id, system_name)

        self.assertTrue(project_id_qs.exists(), system_name +
                        ' was not updated after provisioning new project')
        self.assertEqual(len(project_id_qs), 1,
                         'More than one project_id found for ' + system_name)
        self.assertEqual(project_id_qs.all()[0].identifier,
                         system_data_to_add.get('identifier', None),
                         'ProjectId value in DB does not match input value')

    def test_provision_NeCTAR_UUID_fail(self):
        system_name = 'NeCTAR_UUID'
        response = self._preProvisionSetup(system_name)

        provision_response, proj_data_response = \
            self.provisionGivenProjectResponse(
                self.provisioner_name, response, getProjectDataFlag=True,
                project_provision_success_flag=False, debug=False)

        # Request status will update based on product request, not on project
        # provisioning result
        self._checkProjectRequestStatusCode(
            proj_data_response, REQUEST_STATUS_PROVISIONED)

        self._verify_project_provisioning_details(
            proj_data_response,
            expected_provision_status=ProvisionDetails.FAILED,
            project_sent_for_provisioning_flag=True)

    def test_update_provision_success_before_sending_out_for_provisioning(
            self):
        system_name = 'NeCTAR_UUID'
        response = self._preProvisionSetup(system_name)

        provisioner, list_response = self._get_provisioner(
            self.provisioner_name, make_ready_for_provisioning_flag=False)
        self._provision_project_request(
            provisioner,
            response,
            getProjectDataFlag=False,
            project_provision_success_flag=True,
            expected_provision_response_code=status.HTTP_400_BAD_REQUEST,
            expected_provision_request_status_code=REQUEST_STATUS_PROVISIONED,
            debug=False)

    def test_get_provision_list_after_extend_approve(self):
        testCount = self.PROVISION_LIST_POST_APPROVE_PROVISION_PROJECT
        response = self.flowUpTo(testCount)
        msg = 'Provision List fail for post update Provisioned Project'
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg)

    def test_get_provision_after_extend_approve(self):
        testCount = self.PROVISION_APPROVED_UPDATED_PROVISIONED_PROJECT
        response = self.flowUpTo(testCount)
        msg = 'Provision List fail for post update Provisioned Project'
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg)
