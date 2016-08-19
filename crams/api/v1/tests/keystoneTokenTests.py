from django.test import TestCase
from crams.lang_utils import strip_lower
from crams.api.v1.views import _get_crams_token_for_keystone_user
from crams.api.v1.utils import get_random_string, power_set_generator
from crams.models import CramsToken
from json import loads as json_loads
from crams.roleUtils import ROLE_FB_MAP, generate_project_role


class DummyKeystoneRole:
    def __init__(self, name):
        self.name = name
        self.id = get_random_string(16)


class KeystoneTokenTest(TestCase):
    def setUp(self):
        self.proj_list = ['ProJect_1', 'pRojeCt_2', 'PROJECT_3']

        self.non_fb_role_names = ['Member', 'TenantManager']
        self.fb_role_names = list(ROLE_FB_MAP.keys())

    def generate_token_ks_user(self, role_list):
        self.assertTrue(isinstance(role_list, list), 'role list expected')
        for r in role_list:
            self.assertTrue(isinstance(r, DummyKeystoneRole),
                            'expected DummyKeystoneRole object')
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
        role_names = self.non_fb_role_names + self.fb_role_names
        self.fb_roles_common(role_names)

    def test_project_roles_are_appended_to_project(self):
        role_names = self.non_fb_role_names + self.fb_role_names
        db_roles = self.fb_roles_common(role_names)
        for role in self.non_fb_role_names:
            self.assertFalse(role in db_roles,
                             'Project role must be prefixed with project_ : {}'
                             .format(role))
            for p in self.proj_list:
                project_role = strip_lower(generate_project_role(p, role))
                self.assertTrue(
                    project_role in db_roles,
                    'Project role not found: {} : {}'.format(project_role,
                                                             db_roles))

    def test_admin_roles_must_be_case_insensitive(self):
        mixed_case_role_names = [r.swapcase().title()
                                 for r in self.fb_role_names]
        self.fb_roles_common(mixed_case_role_names)

    def fb_roles_common(self, role_names):
        self.assertTrue(isinstance(role_names, list),
                        'role name list expected')
        for r in role_names:
            self.assertTrue(isinstance(r, str),
                            'role name must be a string')

        crams_role_list = [DummyKeystoneRole(name=r) for r in role_names]
        ks_user = self.generate_token_ks_user(crams_role_list)
        request = None
        # test
        crams_token = _get_crams_token_for_keystone_user(request, ks_user)
        self.assertIsNotNone(crams_token)
        self.assertTrue(isinstance(crams_token, CramsToken))
        crams_role_list = json_loads(crams_token.ks_roles)

        # test Funding Body Roles
        for fb_role in ROLE_FB_MAP.keys():
            self.assertTrue(fb_role in crams_role_list,
                            '{} not in role list'.format(fb_role))

        return crams_role_list
