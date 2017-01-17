from crams.api.v1.dataUtils.lookupData import get_provider_obj
from crams.api.v1.serializers.provisionSerializers import \
    UpdateProvisionProjectSerializer
from rest_framework import status

from crams.DBConstants import REQUEST_STATUS_APPROVED
from crams.DBConstants import REQUEST_STATUS_DECLINED
from crams.DBConstants import REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED
from crams.DBConstants import REQUEST_STATUS_UPDATE_OR_EXTEND
from crams.DBConstants import REQUEST_STATUS_PROVISIONED

from crams.models import Project, ProvisionDetails
from crams.api.v1.tests.baseTest import CRAMSApiTstCase, AdminBaseTstCase
from crams.api.v1.tests.baseTest import ProvisionBaseTstCase
from crams.api.v1.utils import get_random_string

from crams.tests import sampleData


class AdminActionData:

    def __init__(self):
        self.adminClass = AdminBaseTstCase()
        self.adminClass.setUp()


class _AbstractCramsBase(CRAMSApiTstCase):

    class Meta:
        abstract = True

    def setUp(self):
        CRAMSApiTstCase.setUp(self)
        self.debug = False

    def _checkProjectRequestStatusCode(
            self,
            response,
            status_expected,
            requestId=None):
        requests = response.data.get(
            'requests', 'No requests returned with Project')
        self.assertIsNotNone(requests)
        for requestData in requests:
            if requestId:
                if requestData.get('id', None) != requestId:
                    continue
            self._checkRequestStatusCode(requestData, status_expected)

    def _checkRequestStatusCode(self, requestData, status_expected):
        request_status = requestData.get('request_status', None)
        self.assertIsNotNone(request_status, 'Request Status is None')
        status_code = request_status.get('code', None)
        self.assertIsNotNone(
            status_code, 'No code returned for request_status')
        self.assertEqual(
            status_code,
            status_expected,
            'New Request, expected ' +
            status_expected +
            ' status got ' +
            status_code)

    @classmethod
    def setup_random_update(cls, project_data, update_fn):
        instances = 4
        cores = 4
        quota = 4000

        project_data['notes'] = get_random_string(
            8) + ' - ' + project_data.get('description', '')
        for request_data in project_data.get("requests", []):
            # update compute
            compute_requests = request_data.get('compute_requests', None)
            if compute_requests:
                count = 0
                for c in compute_requests:
                    count += 1
                    c["instances"] = instances * count
                    c["cores"] = cores * count

            # update storage
            storage_requests = request_data.get('storage_requests', None)
            if storage_requests:
                count = 0
                for s in storage_requests:
                    count += 1
                    s["quota"] = quota * count
        return update_fn(request_data, instances, cores, quota)

    def update_response_data_random(self, project_data, validate_fn=None):
        def update_fn(request_data, instances, cores, quota):
            return self._update_project_common(
                project_data,
                request_data.get('id'),
                instances,
                cores,
                quota,
                validate_fn)

        return self.setup_random_update(project_data, update_fn)

    def _adminRequest(self, in_response, action_data,
                      expected_http_status=status.HTTP_200_OK,
                      getProjectDataFlag=False):

        if self.debug:
            self.pp.pprint(action_data.actionMsg)

        project = in_response.data
        self.assertIsNotNone(project.get('id', None), 'ProjectId is required')
        msg = action_data.actionMsg + ' for project status test'
        admin_response = action_data.adminFn(
            project.get('id', None),
            national_percent=100,
            approval_notes=str(msg),
            expected_http_status=expected_http_status,
            expected_req_status=action_data.expected_req_status.get('status'),
            expected_status_code=action_data.expected_req_status.get('code'))

        if not getProjectDataFlag:
            return admin_response, None

        project_subset = admin_response.data.get('project', None)
        self.assertIsNotNone(
            project_subset,
            'project not returned after ' +
            action_data.actionMsg)
        projectId = project_subset.get('id', None)
        self.assertIsNotNone(
            projectId,
            'No projectId returned after ' +
            action_data.actionMsg)
        out_response_proj_data = self._get_project_data_by_id(projectId)
        if self.debug:
            self.debugResponse(out_response_proj_data,
                               action_data.actionMsg)

        return admin_response, out_response_proj_data

    def _fetch_project_provision_for_provider(
            self, project_id, providerObj):
        self.assertIsNotNone(project_id, 'Project Id is required')
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            self.assertTrue(
                False, 'Project does not exist for id ' + str(project_id))

        return project.linked_provisiondetails.filter(
            provision_details__provider=providerObj)

    def assertStatusValue(self, expected, actual):
        self.assertEqual(expected, actual, 'Expected ' +
                         str(expected) + ' status, got ' + str(actual))

    def createNew(self, debug=False):
        msg = 'Create New'
        if debug:
            self.pp.pprint(msg)
        # create atleast one project/request for testing get
        response = self._create_project_common(self.test_data)
        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED, response.data)
        if debug:
            self.debugResponse(response, msg)
        return response

    def updateSomething(self, in_response, debug=False):
        msg = 'Update first'
        if debug:
            self.pp.pprint(msg)
        out_response = self.update_response_data_random(in_response.data)
        if debug:
            self.debugResponse(out_response, msg)
        return out_response

    def approveRequest(self, in_response,
                       expected_http_status=status.HTTP_200_OK,
                       getProjectDataFlag=False):
        class ApproveActionData(AdminActionData):

            def __init__(self):
                super(ApproveActionData, self).__init__()
                self.actionMsg = 'Approve Request'
                self.expected_req_status = {
                    'code': REQUEST_STATUS_APPROVED, 'status': 'Approved'}
                self.adminFn = self.adminClass._assert_approve_request

        return self._adminRequest(in_response,
                                  action_data=ApproveActionData(),
                                  expected_http_status=expected_http_status,
                                  getProjectDataFlag=getProjectDataFlag)

    def declineRequest(self, in_response,
                       expected_http_status=status.HTTP_200_OK,
                       getProjectDataFlag=False):
        class DeclineActionData(AdminActionData):

            def __init__(self):
                super(DeclineActionData, self).__init__()
                self.actionMsg = 'Decline Request'
                self.expected_req_status = {
                    'code': REQUEST_STATUS_DECLINED, 'status': 'Declined'}
                self.adminFn = self.adminClass._assert_decline_request

        return self._adminRequest(in_response,
                                  action_data=DeclineActionData(),
                                  expected_http_status=expected_http_status,
                                  getProjectDataFlag=getProjectDataFlag)

    def extendDeclineRequest(self, in_response,
                             expected_http_status=status.HTTP_200_OK,
                             getProjectDataFlag=False):
        class ExtendDeclineActionData(AdminActionData):

            def __init__(self):
                super(ExtendDeclineActionData, self).__init__()
                self.actionMsg = 'Extend/Decline Request'
                self.expected_req_status = {
                    'code': REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED,
                    'status': 'Update/Extension Declined'}
                self.adminFn = self.adminClass._assert_decline_request

        return self._adminRequest(in_response,
                                  action_data=ExtendDeclineActionData(),
                                  expected_http_status=expected_http_status,
                                  getProjectDataFlag=getProjectDataFlag)


class BaseCramsFlow(_AbstractCramsBase):
    def setUp(self, user=None):
        _AbstractCramsBase.setUp(self)
        self.test_data = None
        self.provisioner_name = None
        if user:
            self.user = user
            self.user_contact.email = user.email
            self.user_contact.save()

    # def _debugProjectData(self, proj_data):
    #     print('@@@@@ ', proj_data.get('id'), 'project ',
    #           proj_data.get('title'))
    #     for r in proj_data.get('requests'):
    #         self.pp.pprint(r)

    CREATE_NEW_PROJECT = 1  # 1.  Create New Request
    NEW_PROJECT_TO_SUBMITTED = 2  # 2.  Update Something
    # 3. Decline a request with status 'S' and return response
    SUBMITTED_TO_DECLINE = 3
    # 3.1.  Decline a request wuth status 'S' and return project data on
    # successfull decline
    SUBMITTED_TO_DECLINE_RETURN_PROJECT = 3.1
    # 3.2.  Update successful after Decline status and new request status is
    # 'S', return project data
    UPDATE_DECLINED_PROJECT_RETURN_PROJECT_DATA = 3.2
    SUBMITTED_TO_APPROVE = 4  # 4.  Approve and return approve Response
    # 4.1.  Approve a request wuth status 'S' and return project data on
    # successfull approve
    SUBMITTED_TO_APPROVE_RETURN_PROJECT = 4.1
    # 4.2.  Update should fail after approve of status 'S'
    UPDATE_FAIL_FOR_APPROVE_STATUS = 4.2
    # 5.  Provision given project response and return provision_response
    PROVISION_PROJECT_RETURN_RESPONSE = 5
    # 5.1.  Provision given project and return project data on successful
    # provision
    PROVISION_PROJECT_RETURN_PROJECT = 5.1
    # 6.  Update a Project with all Provisioned Request and return project data
    UPDATE_PROVISIONED_PROJECT_RETURN_PROJECT = 6
    # 7.  Approve a previously provisioned and edited project
    APPROVE_UPDATED_PROVISIONED_PROJECT = 7
    # 8.  Second time Provisioning list, return list response
    PROVISION_LIST_POST_APPROVE_PROVISION_PROJECT = 8
    # 8.1.  Second time Provisioning of an updated and approved request
    PROVISION_APPROVED_UPDATED_PROVISIONED_PROJECT = 8.1

    def flowUpTo(self, flowCount, debug=False):
        self.debug = debug
        response1 = self.createNew()
        if flowCount <= self.CREATE_NEW_PROJECT:
            return response1

        # update something
        response2 = self.updateSomething(response1)
        if flowCount <= self.NEW_PROJECT_TO_SUBMITTED:
            return response2

        if flowCount < self.SUBMITTED_TO_APPROVE:
            declineResponse, proj_data_response = self.declineRequest(
                response2, getProjectDataFlag=True)
            if flowCount == self.SUBMITTED_TO_DECLINE:
                return declineResponse
            if flowCount == self.UPDATE_DECLINED_PROJECT_RETURN_PROJECT_DATA:
                return self.updateSomething(proj_data_response)
            return proj_data_response

        # approve request
        approve_response, response3 = self.approveRequest(
            response2, getProjectDataFlag=True)
        if flowCount == self.SUBMITTED_TO_APPROVE:
            return approve_response
        if flowCount == self.SUBMITTED_TO_APPROVE_RETURN_PROJECT:
            return response3

        # update again
        msg = 'Update after approve, should fail'

        def _update_fail_fn(response):
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                'update after approve should fail : {}'.format(
                    response.data))

        if debug:
            self.pp.pprint(msg)
        error_response = self.update_response_data_random(
            response3.data, _update_fail_fn)
        if flowCount == self.UPDATE_FAIL_FOR_APPROVE_STATUS:
            return error_response

        if not self.provisioner_name:
            return ValueError('provisioner Name is required')

        if debug:
            print('**** First Provision after Approve')
        provision_response, proj_data_response = \
            self.provisionGivenProjectResponse(
                self.provisioner_name, response3,
                getProjectDataFlag=True, debug=debug)
        self._verify_db_project_provisioning_details(
            proj_data_response,
            expected_provision_status=ProvisionDetails.PROVISIONED)

        if flowCount == self.PROVISION_PROJECT_RETURN_RESPONSE:
            return provision_response
        if flowCount == self.PROVISION_PROJECT_RETURN_PROJECT:
            return proj_data_response

        if debug:
            print('**** before update after First Provision after Approve')

        edit_response = \
            self.update_response_data_random(proj_data_response.data)
        self._checkProjectRequestStatusCode(
            edit_response, REQUEST_STATUS_UPDATE_OR_EXTEND)

        self._verify_db_project_provisioning_details(
            edit_response,
            expected_provision_status=ProvisionDetails.POST_PROVISION_UPDATE
        )
        if debug:
            print('**** after update after First Provision after Approve')

        if flowCount <= self.UPDATE_PROVISIONED_PROJECT_RETURN_PROJECT:
            return edit_response

        # approve request again
        approve_response, response4 = self.approveRequest(
            edit_response, getProjectDataFlag=True)

        self._verify_db_project_provisioning_details(
            self._get_project_data_by_id(response4.data.get('id')),
            expected_provision_status=ProvisionDetails.POST_PROVISION_UPDATE
        )

        if flowCount <= self.APPROVE_UPDATED_PROVISIONED_PROJECT:
            return approve_response

        if debug:
            print('**** Second Provision list after Approve')

        # Get Provision List and then check Project to see status updated X
        provisioner, list_response = self._get_provisioner(
            self.provisioner_name, make_ready_for_provisioning_flag=True)

        update_sent = ProvisionDetails.POST_PROVISION_UPDATE_SENT
        self._verify_db_project_provisioning_details(
            self._get_project_data_by_id(response4.data.get('id')),
            expected_provision_status=update_sent
        )

        if flowCount <= self.PROVISION_LIST_POST_APPROVE_PROVISION_PROJECT:
            return list_response

        if debug:
            print('**** Second Provision complete after Approve')

        provision_response, proj_data_response = \
            self.provisionGivenProjectResponse(
                self.provisioner_name, response4,
                getProjectDataFlag=True, debug=debug)

        self._verify_db_project_provisioning_details(
            proj_data_response,
            expected_provision_status=ProvisionDetails.PROVISIONED)
        if flowCount <= self.PROVISION_APPROVED_UPDATED_PROVISIONED_PROJECT:
            return proj_data_response

        return proj_data_response

    def _verify_db_project_provisioning_details(
            self,
            proj_data_response,
            expected_provision_status=None,
            project_sent_for_provisioning_flag=True):

        project_id = proj_data_response.data.get('id', None)
        self.assertIsNotNone(
            project_id, 'Project data returned has null value for id')
        providerObj = get_provider_obj({'name': self.provisioner_name})
        provision_details_qs = self._fetch_project_provision_for_provider(
            project_id, providerObj)
        if project_sent_for_provisioning_flag:
            self.assertTrue(
                provision_details_qs.exists(),
                'Project Provision details for provider {} should exist after '
                'provision attempt'.format(
                    repr(providerObj)))
            self.assertEqual(
                len(provision_details_qs),
                1,
                'More than one provision detail found for provider {}'.format(
                    repr(providerObj)))
            pp = provision_details_qs.all()[0]
            error_msg = 'Project Provision detail not updated to {} status ' \
                        'id {} - {}'.format(repr(expected_provision_status),
                                            repr(pp.id),
                                            repr(pp.provision_details))
            self.assertEqual(pp.provision_details.status,
                             expected_provision_status,
                             error_msg)
        else:
            self.assertFalse(
                provision_details_qs.exists(),
                'Project Provision details should not exist until project is '
                'sent for provisioning or update')

    def _get_provisioner(
            self,
            provisionerName,
            make_ready_for_provisioning_flag=True):
        # Initialize and get provisioner ready
        provisioner = ProvisionBaseTstCase()
        provisioner.setUp()
        provisioner.setUserProviderFor(provisionerName)

        listResponse = None
        if make_ready_for_provisioning_flag:
            listResponse = provisioner._returnFetchProvisionListResponse()
            # for l in listResponse.data:
            #     print('list provision ====', l.get('id'), l.get('title'),
            # '========', len(l.get('requests')))
            #     #self.pp.pprint(l.get('requests'))
            self.assertEqual(listResponse.status_code,
                             status.HTTP_200_OK, listResponse.data)
            self.assertTrue(len(listResponse.data) > 0,
                            'No data, cannot make ready for provisioning, ' +
                            'user: ' + repr(self.user))

        return provisioner, listResponse

    def _provision_project_request(
            self,
            provisioner,
            in_response,
            getProjectDataFlag=False,
            project_provision_success_flag=True,
            expected_provision_response_code=status.HTTP_201_CREATED,
            expected_provision_request_status_code=REQUEST_STATUS_PROVISIONED,
            debug=False):
        provisionData = UpdateProvisionProjectSerializer(
        )._init_from_project_data(in_response.data)
        if not project_provision_success_flag:
            provisionData['success'] = False
            provisionData['message'] = 'Project Provisioning Failed'

        provisionResponse = provisioner._returnProvisionUpdateResponse(
            provisionData)
        self.assertEqual(
            provisionResponse.status_code,
            expected_provision_response_code,
            provisionResponse.data)
        if not getProjectDataFlag:
            return provisionResponse, None

        projectId = provisionResponse.data.get('id', None)
        self.assertIsNotNone(
            projectId, 'Provision project returned null project id')
        out_proj_data = self._get_project_data_by_id(projectId)
        self._checkProjectRequestStatusCode(
            out_proj_data, expected_provision_request_status_code)

        return provisionResponse, out_proj_data

    def provisionGivenProjectResponse(
            self,
            provisionerName,
            in_response,
            getProjectDataFlag=False,
            project_provision_success_flag=True,
            expected_provision_response_code=status.HTTP_201_CREATED,
            expected_provision_request_status_code=REQUEST_STATUS_PROVISIONED,
            debug=False):
        msg = 'Provision First and Test Status'
        if debug:
            self.pp.pprint(msg)

        provisioner, list_response = self._get_provisioner(
            provisionerName, make_ready_for_provisioning_flag=True)
        # print('<-------------','In Response ',  in_response.data.get('id'),
        # in_response.data.get('Title'), len(in_response.data.get('requests')))
        # #self.pp.pprint(in_response.data.get('requests'))
        return self._provision_project_request(
            provisioner,
            in_response,
            getProjectDataFlag,
            project_provision_success_flag,
            expected_provision_response_code,
            expected_provision_request_status_code,
            debug)


class NectarCramsFlow:
    def __init__(self, user=None):
        flow_obj = BaseCramsFlow()
        flow_obj.setUp(user)
        self.flow_obj = flow_obj

    def flow_upto(self, flow_count):
        # setup new test data
        self.flow_obj.test_data = sampleData.get_base_nectar_project_data(
            self.flow_obj.user.id, self.flow_obj.user_contact)
        return self.flow_obj.flowUpTo(flow_count)
