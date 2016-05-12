from rest_framework import status

from crams.DBConstants import *
from crams.dbUtils import get_request_status_lookups
from tests.sampleData import get_base_nectar_project_data
from tests.sampleData import get_vicnode_test_data
from crams.api.v1.tests.baseCramsFlow import BaseCramsFlow
from crams.api.v1.utils import get_random_string

__author__ = 'rafi m feroze'  # 'mmohamed'


class NectarRequestStatusTests(BaseCramsFlow):

    def setUp(self):
        BaseCramsFlow.setUp(self)
        self.test_data = get_base_nectar_project_data(self.user.id,
                                                      self.contact)
        self.provisioner_name = 'NeCTAR'
        self.requestStatusLookups = get_request_status_lookups()

    def test_new_nectar_request_status_is_submitted(self):
        testCount = self.CREATE_NEW_PROJECT
        response = self.flowUpTo(testCount)
        self._checkProjectRequestStatusCode(response, REQUEST_STATUS_SUBMITTED)

    def test_updated_request_status_is_submitted_before_approval(self):
        testCount = self.NEW_PROJECT_TO_SUBMITTED
        response = self.flowUpTo(testCount)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, 'Update before Approve fail')
        self._checkProjectRequestStatusCode(response, REQUEST_STATUS_SUBMITTED)

    def test_submitted_to_decline_status(self):
        testCount = self.SUBMITTED_TO_DECLINE
        response = self.flowUpTo(testCount)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)
        statusValue = response.data.get('request_status', None)
        expectedStatus = self.requestStatusLookups.get(
            REQUEST_STATUS_DECLINED).status
        self.assertStatusValue(expectedStatus, statusValue)

    def test_decline_to_submitted_status(self):
        testCount = self.UPDATE_DECLINED_PROJECT_RETURN_PROJECT_DATA
        response = self.flowUpTo(testCount)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)
        self._checkProjectRequestStatusCode(response, REQUEST_STATUS_SUBMITTED)

    def test_updated_request_status_is_Approved_on_first_approval(self):
        testCount = self.SUBMITTED_TO_APPROVE
        response = self.flowUpTo(testCount)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)
        statusValue = response.data.get('request_status', None)
        expectedStatus = self.requestStatusLookups.get(
            REQUEST_STATUS_APPROVED).status
        self.assertStatusValue(expectedStatus, statusValue)

    def test_approve_to_edit_fails_before_provisioning(self):
        testCount = self.UPDATE_FAIL_FOR_APPROVE_STATUS
        self.flowUpTo(testCount)

    def test_status_moves_to_provision_after_first_approve(self):
        testCount = self.PROVISION_PROJECT_RETURN_PROJECT
        response = self.flowUpTo(testCount)
        self._checkProjectRequestStatusCode(
            response, REQUEST_STATUS_PROVISIONED)

    def test_fail_update_static_fields_after_approve(self):
        def _updateFailFn(response):
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                'update after approve for description should fail : {}'.format(
                    response.data))

        testCount = self.PROVISION_PROJECT_RETURN_PROJECT
        response = self.flowUpTo(testCount)
        project = response.data
        project['description'] = 'New Description ' + get_random_string(64)
        self._updateResponseDataRandom(project, _updateFailFn)

    def test_decline_to_approval_fails_without_edit(self):
        testCount = self.SUBMITTED_TO_DECLINE_RETURN_PROJECT
        decline_proj_response = self.flowUpTo(testCount)
        self.approveRequest(decline_proj_response,
                            status.HTTP_404_NOT_FOUND,
                            False)
        editResponse = self._updateResponseDataRandom(
            decline_proj_response.data)
        self.approveRequest(editResponse, status.HTTP_200_OK, False)

    def test_provisioned_to_update_extended_status_success(self):
        testCount = self.PROVISION_PROJECT_RETURN_PROJECT
        provision_proj_response = self.flowUpTo(testCount)
        editResponse = self._updateResponseDataRandom(
            provision_proj_response.data)
        self._checkProjectRequestStatusCode(
            editResponse, REQUEST_STATUS_UPDATE_OR_EXTEND)

    def test_update_extended_to_approve_success(self):
        testCount = self.UPDATE_PROVISIONED_PROJECT_RETURN_PROJECT
        editResponse = self.flowUpTo(testCount)
        approved_response, approved_project = self.approveRequest(
            editResponse, getProjectDataFlag=True)
        self._checkProjectRequestStatusCode(
            approved_project, REQUEST_STATUS_APPROVED)
        return approved_project

    def test_status_moves_to_provision_after_subsequent_approvals(self):
        approved_project = self.test_update_extended_to_approve_success()

        provision_response, proj_data_response = \
            self.provisionGivenProjectResponse(self.provisioner_name,
                                               approved_project,
                                               getProjectDataFlag=True,
                                               debug=False)
        self._checkProjectRequestStatusCode(
            proj_data_response, REQUEST_STATUS_PROVISIONED)

    def test_update_extend_to_update_extend_decline(self):
        testCount = self.UPDATE_PROVISIONED_PROJECT_RETURN_PROJECT
        editResponse = self.flowUpTo(testCount)
        declined_response, declined_project = self.extendDeclineRequest(
            editResponse, getProjectDataFlag=True)
        self._checkProjectRequestStatusCode(
            declined_project, REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED)
        return declined_project

    def test_extended_decline_to_update_extended_success(self):
        declined_project = self.test_update_extend_to_update_extend_decline()
        editResponse = self._updateResponseDataRandom(declined_project.data)
        self._checkProjectRequestStatusCode(
            editResponse, REQUEST_STATUS_UPDATE_OR_EXTEND)
        return editResponse

    def test_update_extended_cycle_on_update(self):
        response = self.test_extended_decline_to_update_extended_success()
        editResponse = self._updateResponseDataRandom(response.data)
        self._checkProjectRequestStatusCode(
            editResponse, REQUEST_STATUS_UPDATE_OR_EXTEND)

    def test_extended_decline_to_approve_fails_without_edit(self):
        declined_project = self.test_update_extend_to_update_extend_decline()
        self.extendDeclineRequest(
            declined_project,
            expected_http_status=status.HTTP_404_NOT_FOUND,
            getProjectDataFlag=False)


class VicnodeRequestStatus(BaseCramsFlow):

    def setUp(self):
        BaseCramsFlow.setUp(self)
        self.provisioner_name = 'Vicnode'
        self.requestStatusLookups = get_request_status_lookups()
        # override default Nectar test_data
        self.test_data = get_vicnode_test_data(self.user.id, self.contact)

    def test_new_vicnode_request_status_is_new(self):
        testCount = self.CREATE_NEW_PROJECT
        response = self.flowUpTo(testCount)
        self._checkProjectRequestStatusCode(response, REQUEST_STATUS_NEW)

    def test_new_status_changes_to_submitted_on_update(self):
        testCount = self.NEW_PROJECT_TO_SUBMITTED
        response = self.flowUpTo(testCount)
        self._checkProjectRequestStatusCode(response, REQUEST_STATUS_SUBMITTED)

    # No additional Tests Required
