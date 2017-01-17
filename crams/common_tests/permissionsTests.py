from crams.api.v1.tests.baseTest import CRAMSApiTstCase
from crams.api.v1.views import ProjectViewSet
from crams.models import Request, Project
from crams.permissions import IsProjectContact
from crams.permissions import IsRequestApprover, IsActiveProvider
from crams.roleUtils import FB_ROLE_MAP_REVERSE
from crams.settings import CRAMS_PROVISIONER_ROLE
from crams.tests import sampleData


class PermissionsTest(CRAMSApiTstCase):
    def setUp(self):
        CRAMSApiTstCase.setUp(self)
        self.http_request = self.factory.get('api/project')
        self.test_data = sampleData.get_base_nectar_project_data(
            self.user.id, self.user_contact)

    def _set_roles(self, roleList):
        self.set_user_roles(roleList)
        self.http_request.user = self.user

    def test_is_project_contact(self):
        self._create_project_common(self.test_data)
        view = ProjectViewSet.as_view({'get': 'list', 'post': 'create'})
        valid_user = self.user
        invalid_user = self.get_new_user('randomUser',
                                         'dummy@permissions.test')

        for project in Project.objects.filter(
                project_contacts__contact__email=self.user.email):
            # Valid Contact Test
            self.http_request.user = valid_user
            bool = IsProjectContact().has_object_permission(
                self.http_request, view, project)
            self.assertTrue(bool, '{}: not a contact for project {}'
                            .format(self.user, project))
            # inValid Contact Test
            self.http_request.user = invalid_user
            bool = IsProjectContact().has_object_permission(
                self.http_request, view, project)
            self.assertFalse(
                bool,
                '{}: should not be a contact for project {}'.format(
                    self.user, project)
            )

    def test_is_approver(self):
        self._create_project_common(self.test_data)
        view = ProjectViewSet.as_view({'get': 'list', 'post': 'create'})
        for (fb, role) in FB_ROLE_MAP_REVERSE.items():
            request_obj_qs = Request.objects.filter(
                funding_scheme__funding_body__name=fb)
            if request_obj_qs.exists():
                req = request_obj_qs.first()
                # Test Valid Role
                self._set_roles([role])
                bool = IsRequestApprover().has_object_permission(
                    self.http_request, view, req)
                self.assertTrue(bool, '{}: not an approver for request {}'
                                .format(fb, req))
                # Test Case insensitive role
                self._set_roles([role.upper()])
                bool = IsRequestApprover().has_object_permission(
                    self.http_request, view, req)
                self.assertTrue(bool, '{}: not an approver for request {}'
                                .format(fb, req))
                # Test invalid Role
                new_roles = set(FB_ROLE_MAP_REVERSE.values())
                new_roles.remove(role)
                self._set_roles(list(new_roles))
                bool = IsRequestApprover().has_object_permission(
                    self.http_request, view, req)
                self.assertFalse(bool, '{}: should not be an approver for '
                                       'request {}'.format(fb, req))
            # else:
            #     print('Request object not found for FB', fb)

    def test_is_provisioner(self):
        # Setup Provisioner Role
        self._set_roles([CRAMS_PROVISIONER_ROLE])
        self.http_request.user = self.user
        bool = IsActiveProvider().has_permission(self.http_request, None)
        self.assertTrue(bool, 'Expected isActiveProvider, got false')

        # Test without Crams Provisioner Role
        self._set_roles(list(FB_ROLE_MAP_REVERSE.values()))
        self.http_request.user = self.user
        bool = IsActiveProvider().has_permission(self.http_request, None)
        self.assertFalse(bool, 'Expected not isActiveProvider, got yes')

        # Setup case senstive Provisioner Role
        self._set_roles([CRAMS_PROVISIONER_ROLE.upper()])
        self.http_request.user = self.user
        bool = IsActiveProvider().has_permission(self.http_request, None)
        self.assertTrue(bool, 'Expected isActiveProvider, got false')
