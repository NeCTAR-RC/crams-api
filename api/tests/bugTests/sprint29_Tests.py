from rest_framework import status
from api.tests.baseTest import CRAMSApiTstCase
from crams.models import FundingBody
from api.utils import power_set_generator, compare_two_lists_or_sets
from api.views_list import CurrentUserApproverRoleList
from crams.DBConstants import APPROVER_APPEND_STR

__author__ = 'rafi m feroze'  # 'mmohamed'


class Bug_740_TestCase(CRAMSApiTstCase):

    def setUp(self):
        CRAMSApiTstCase.setUp(self)

    def getUserRolesAPIResponse(self):
        view = CurrentUserApproverRoleList.as_view({'get': 'list'})
        request = self.factory.get('api/user_funding_body')
        request.user = self.user
        return view(request)

    def test_powerSet_generator_util_method(self):
        testList = set(['NecTAR', 'Vicnode', 'NCI'])
        actualList = list(power_set_generator(testList))
        expectedList = [
            set(), {'Vicnode'}, {'NCI'}, {'NecTAR'}, {
                'Vicnode', 'NCI'}, {
                'Vicnode', 'NecTAR'}, {
                'NCI', 'NecTAR'}, {
                    'Vicnode', 'NCI', 'NecTAR'}]
        self.assertTrue(compare_two_lists_or_sets(expectedList, actualList),
                        'Expected powerset does not match returned powerset')

    # def printUserRoles(self, request):
    #     userRoles = []
    #     user = User.objects.get(pk=request.user.id)
    #     jsonRoles = user.auth_token.cramstoken.ks_roles
    #     if jsonRoles:
    #         userRoles = json_loads(jsonRoles)
    #
    #     print('after set, found ' , request.user, userRoles)

    def test_user_with_no_approver_roles(self):
        cramsToken = self.user.auth_token.cramstoken
        cramsToken.ks_roles = None
        cramsToken.save()
        response = self.getUserRolesAPIResponse()
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data), 0,
                         'User should not have any approver roles, got {}'.
                         format(repr(response.data)))

    def test_funding_body_user_list_for_all_combinations_except_none(self):
        def appendApproverStr(fbList):
            ret_list = []
            for fb in fbList:
                ret_list.append(fb.lower() + APPROVER_APPEND_STR)
            return ret_list

        fbNameList = FundingBody.objects.all().values_list('name', flat=True)

        for sampleSet in power_set_generator(fbNameList):
            if len(sampleSet) > 0:
                userRoles = appendApproverStr(sampleSet)
                self._setUserRoles(userRoles)

                response = self.getUserRolesAPIResponse()
                self.assertEqual(response.status_code,
                                 status.HTTP_200_OK, response.data)

                responseFbNames = set()
                for fbDict in response.data:
                    responseFbNames.add(fbDict.get('name', None))
                self.assertTrue(
                    responseFbNames == sampleSet,
                    'Did not return expected funding body list for user')

        # sampleResponse = [   {'approver': True, 'id': 3,
        #                       'name': 'Intersect'},
        #     {'approver': True, 'id': 5, 'name': 'Monash'},
        #     {'approver': True, 'id': 6, 'name': 'NCI'},
        #     {'approver': True, 'id': 1, 'name': 'NeCTAR'},
        #     {'approver': True, 'id': 7, 'name': 'Pawsey'},
        #     {'approver': True, 'id': 8, 'name': 'QCIF'},
        #     {'approver': True, 'id': 10, 'name': 'TPAC'},
        #     {'approver': True, 'id': 4, 'name': 'UoM'},
        #     {'approver': True, 'id': 2, 'name': 'VicNode'},
        #     {'approver': True, 'id': 9, 'name': 'eRSA'}]
