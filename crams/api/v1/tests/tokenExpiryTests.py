import datetime
from rest_framework import status

from crams.api.v1.tests.baseTest import CRAMSApiTstCase
from crams.settings import TOKEN_EXPIRY_TIME_MINUTES
from crams.api.v1 import views
from crams.api.v1 import views_list
from crams.api.v1 import projectRequestListAPI as pr_api


class CramsTokenExpiryTests(CRAMSApiTstCase):
    def setUp(self):
        CRAMSApiTstCase.setUp(self)
        # Expire Token
        setback_ts = datetime.timedelta(minutes=TOKEN_EXPIRY_TIME_MINUTES)
        self.token.created = self.token.created - setback_ts
        self.token.save()

        self.viewset_api_dict = {
            'project/': views.ProjectViewSet,
            'request_history/': views_list.RequestHistoryViewSet,
            'request/': views.RequestViewSet,
            'approve_request/': views.ApproveRequestViewSet,
            'decline_request/': views.DeclineRequestViewSet,
            'provision_project/list/': views.ProvisionProjectViewSet,
            'provision_project/update/': views.UpdateProvisionProjectViewSet,
            'provision_request/': views.ProvisionRequestViewSet,
            'user_funding_body': views_list.CurrentUserApproverRoleList,
            'contact': views.ContactViewSet,

        }
        self.view_dict = {
            'user_roles': views_list.CurrentUserRolesView,
            'contact/junk@mail.edu': views.ContactDetail,
            'searchcontact': views.SearchContact,
            'project_list': pr_api.UserProjectListView,
            'project_request_list': pr_api.UserProjectRequestListView,
            'approve_list': pr_api.ApproverReviewerRequestListView,
            'alloc_counter': pr_api.FundingBodyAllocationsCounter,
        }

        self.view_fn_dict = {
            # 'contacts': lookup.contacts,
        }

    def test_expired_token(self):
        # Rest Viewsets
        for (url, cls) in self.viewset_api_dict.items():
            # list APIs
            view = cls.as_view({'get': 'list'})
            response = self._baseGetAPI(view, url, None)
            self.validate_response(url, response)
            # detail APIs
            response = self._baseGetAPI(view, url, 1)
            self.validate_response(url, response, True)
            # create APIs
            try:
                view = cls.as_view({'get': 'list', 'put': 'create'})
                response = self.base_put_api(view, url, {}, None)
                self.validate_response(url, response)
            except AttributeError:
                pass  # Not all viewsets allow create

            # update APIs
            try:
                view = cls.as_view({'get': 'retrieve', 'put': 'update'})
                response = self.base_put_api(view, url, {}, 1)
                self.validate_response(url, response)
            except AttributeError:
                pass  # Not all viewsets allow update

        # Rest Views
        for (url, cls) in self.view_dict.items():
            view = cls.as_view()
            response = self._baseGetAPI(view, url, None)
            self.validate_response(url, response)

        # Django View Functions
        for (url, view_fn) in self.view_fn_dict.items():
            response = self._baseGetAPI(view_fn, url, None)
            self.validate_response(url, response)

    def validate_response(self, url, response, is_detail=False):
        err = 'Expired Token error: {} - '.format(url)
        if is_detail:
            err = 'Expired Token error: {}'.format(url + '/1')

        self.assertIsNotNone(response.data, 'Data None: {}'.format(err))
        self.assertTrue(type(response.data) == dict, err +
                        'Expected Dict, got {}'.format(repr(response.data)))
        exception_msg = response.data.get('detail')
        self.assertIsNotNone(exception_msg, 'Expected msg: {}'.format(err))
        expected_msg = 'User does not hold valid CramsToken.'
        detail_err = 'expected {} / got {} : {}'.format(exception_msg,
                                                        expected_msg,
                                                        err)
        self.assertEqual(exception_msg, expected_msg, detail_err)
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED, err)
