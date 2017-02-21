from crams.api.v1.views_list import CurrentUserApproverRoleList
from rest_framework import status

from crams.roleUtils import FB_ROLE_MAP_REVERSE
from crams.api.v1.tests.baseTest import CRAMSApiTstCase
from crams.api.v1.utils import power_set_generator, compare_two_lists_or_sets


class Bug_740_TestCase(CRAMSApiTstCase):

    def setUp(self):
        CRAMSApiTstCase.setUp(self)

    def getUserRolesAPIResponse(self):
        view = CurrentUserApproverRoleList.as_view({'get': 'list'})
        request = self.factory.get('api/user_funding_body')
        request.user = self.user
        response = view(request)
        return response

    def test_powerSet_generator_util_method(self):
        testList = set(['NecTAR', 'TPAC', 'NCI'])
        actualList = list(power_set_generator(testList))
        expectedList = [
            set(), {'TPAC'}, {'NCI'}, {'NecTAR'}, {
                'TPAC', 'NCI'}, {
                'TPAC', 'NecTAR'}, {
                'NCI', 'NecTAR'}, {
                    'TPAC', 'NCI', 'NecTAR'}]
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
        fb_name_list = FB_ROLE_MAP_REVERSE.keys()
        for sampleSet in power_set_generator(fb_name_list):
            if len(sampleSet) > 0:
                user_roles = [FB_ROLE_MAP_REVERSE[x] for x in sampleSet]
                self.set_user_roles(user_roles)

                response = self.getUserRolesAPIResponse()
                self.assertEqual(response.status_code,
                                 status.HTTP_200_OK, response.data)

                response_fb_names = set()
                for fbDict in response.data:
                    response_fb_names.add(fbDict.get('name', None))
                self.assertTrue(
                    response_fb_names == sampleSet,
                    'Did not return expected funding body list for user, '
                    'Expected: {}/Got: {}'.format(sampleSet, response_fb_names)
                )
