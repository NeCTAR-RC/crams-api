from django.test import TestCase
from crams.api.v1.views import _get_crams_token_for_keystone_user
from crams.api.v1.utils import get_random_string, power_set_generator
from crams.models import CramsToken
from json import loads as json_loads
from crams.roleUtils import ROLE_FB_MAP


class DummyKeystoneRole:
    def __init__(self, name):
        self.name = name
        self.id = get_random_string(16)


class KeystoneTokenTest(TestCase):
    def setUp(self):
        self.proj_list = ['project_1', 'project_2', 'project_3']

        self.non_fb_role_names = ['Member', 'TenantManager']
        self.non_fb_roles = [DummyKeystoneRole(name=r)
                             for r in self.non_fb_role_names]
        self.fb_roles = [DummyKeystoneRole(name=r) for r in ROLE_FB_MAP.keys()]

    def generate_token_ks_user(self, role_list):
        ks_user = dict()
        ks_user['name'] = get_random_string(12)
        ks_user['id'] = get_random_string(16)

        roles = dict()
        ks_user['roles'] = roles
        for rs in power_set_generator(role_list):
            for p in self.proj_list:
                roles[p] = list(rs)
        return ks_user

    def test_get_crams_token_for_keystone_user(self):
        role_list = self.non_fb_roles + self.fb_roles
        self.fb_roles_common(role_list)

    def test_project_roles_are_appended_to_project(self):
        role_list = self.non_fb_roles + self.fb_roles
        self.fb_roles_common(role_list)
        for role in self.non_fb_role_names:
            self.assertFalse(role in role_list,
                             'Project role must be prefixed with project_ : {}'
                             .format(role))

    def test_admin_roles_must_be_case_insensitive(self):
        role_list = [DummyKeystoneRole(name=r.swapcase())
                     for r in ROLE_FB_MAP.keys()]
        self.fb_roles_common(role_list)

    def fb_roles_common(self, role_list):
        ks_user = self.generate_token_ks_user(role_list)
        request = None
        # test
        crams_token = _get_crams_token_for_keystone_user(request, ks_user)
        self.assertIsNotNone(crams_token)
        self.assertTrue(isinstance(crams_token, CramsToken))
        role_list = json_loads(crams_token.ks_roles)

        # test Funding Body Roles
        for fb_role in ROLE_FB_MAP.keys():
            self.assertTrue(fb_role in role_list,
                            '{} not in role list'.format(fb_role))
