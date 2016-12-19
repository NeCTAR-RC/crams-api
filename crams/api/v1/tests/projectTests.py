from rest_framework import status

from crams import dbUtils
from crams.models import Contact, CramsToken
from tests import sampleData
from tests.sampleData import get_project_only_no_request_data
from crams.api.v1.tests.baseTest import CRAMSApiTstCase
from crams.api.v1.tests.baseCramsFlow import _AbstractCramsBase
from crams.api.v1.views import ProjectViewSet
from crams import settings
from crams import DBConstants
from crams.api.v1 import utils as api_utils
from crams.api.v1.validators import projectid_validators
from crams import roleUtils


class ProjectViewSetTest(CRAMSApiTstCase):
    fixtures = ['v1/test_common_data']

    def test_project_fetch(self):
        view = ProjectViewSet.as_view({'get': 'list', 'post': 'create'})
        project_data = get_project_only_no_request_data(self.user.id,
                                                        self.user_contact)
        request = self.factory.post('api/project', project_data)
        request.user = self.user

        response = view(request)

        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED, response.data)
        self.assertIsNot(response.data.get("id"), 0, response.data)
        self.assertEqual(response.data.get("title"),
                         project_data.get("title"), response.data)


class BaseProjectTests(_AbstractCramsBase):
    def setUp(self, test_data_fn, provisioner_name):
        _AbstractCramsBase.setUp(self)
        self.contact_email = 'newContact@monash.edu'
        self.user_contact, created = Contact.objects.get_or_create(
            title='Mr', given_name='Test', surname='MeRC',
            email=self.contact_email,
            phone='99020780', organisation='Monash University')

        self.generate_test_data_fn = test_data_fn
        self.test_data = self.generate_test_data_fn(self.user.id,
                                                    self.user_contact)

        self.provisioner_name = provisioner_name
        self.requestStatusLookups = dbUtils.get_request_status_lookups()
        self.system_id_map = dbUtils.get_system_name_map()

    def validate_concurrent_project_update(self):
        def validate_update_fail_fn(response):
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                'concurrent update should fail : {}'.format(
                    response.data))
            expected_msg = 'concurrent update: <User: newContact@monash.edu>' \
                           ' has updated project, please refresh and try again'
            self.assertEqual(response.data.get('detail'),
                             expected_msg,
                             'Concurrent Error messages do not match')

        contact_user = self.get_new_user('randomUser', self.contact_email)
        contact_token, created = CramsToken.objects.get_or_create(
            user=contact_user)
        self.test_data = self.generate_test_data_fn(self.user.id,
                                                    self.user_contact)

        response = self.createNew()
        originalUser = self.user
        originalToken = self.token

        self.user = contact_user
        self.token = contact_token
        self.updateSomething(response)

        self.user = originalUser
        self.token = originalToken

        def update_fn(request_data, instances, cores, quota):
            view = ProjectViewSet.as_view({'post': 'update'})

            pk = request_data.get('id')
            request = self.factory.post('api/project?request_id=' + str(pk),
                                        request_data)
            request.user = self.user
            response = view(request)
            return validate_update_fail_fn(response)

        self.update_response_data_random(response.data,
                                         validate_update_fail_fn)

    def validate_project_id_prefix(self, project_json,
                                   required_sysid_list=set()):
        # ensure project data has project_ids from required_sysid_list
        self.add_required_project_ids(project_json, required_sysid_list)

        pid_map = settings.PROJECT_SYSTEM_ID_INVALID_PREFIX_MAP
        for pid_json in project_json.get('project_ids'):
            pid_json_copy = projectid_validators.\
                extract_project_id_save_args(pid_json)
            system_name = pid_json.get('system').get('system')
            if system_name in pid_map.keys():
                invalid_prefix_list = pid_map.get(system_name)
                if not invalid_prefix_list:
                    continue
                all_combo_invalid_list = list()
                for base_prefix in invalid_prefix_list:
                    all_combo_invalid_list.extend(
                        api_utils.generate_all_case_combinations(base_prefix))

                for invalid_prefix in all_combo_invalid_list:
                    s_id = invalid_prefix + pid_json_copy.get('identifier')
                    pid_json['identifier'] = s_id
                    response = self._create_project_common(project_json, False)
                    msg = 'sys id cannot begin with: {}'.format(invalid_prefix)
                    self.assertEqual(response.status_code,
                                     status.HTTP_400_BAD_REQUEST,
                                     msg)

    def validate_duplicate_project_id(self, system_name_set):
        project_json = self.generate_test_data_fn(self.user.id, self.contact)
        response = self._create_project_common(project_json, True)

        # Verify project has required System Ids
        project_ids = response.data.get('project_ids')
        system_id_map = dict()
        for pid_json in project_ids:
            system_name = pid_json.get('system').get('system')
            if system_name in system_name_set:
                pid_json.pop('id')
                system_id_map[system_name] = pid_json.get('identifier')
        not_found_set = system_name_set.difference(system_id_map.keys())
        self.assertFalse(not_found_set,
                         'SystemIds not found for ' + ','.join(not_found_set))

        # create a new project json and replace system id's with existing ones
        new_proj_json = self.generate_test_data_fn(self.user.id, self.contact)
        project_ids = new_proj_json.get('project_ids')
        for pid_json in project_ids:
            system_name = pid_json.get('system').get('system')
            if system_name in system_id_map.keys():
                pid_json['identifier'] = system_id_map.get(system_name)
        response = self._create_project_common(project_json, False)
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST,
                         'Duplicate Project Id creation must fail')
        msg = response.data.get('detail')
        self.assertIsNotNone(msg, 'Expected error message')
        self.assertTrue(msg.startswith('Project Id ('),
                        'Invalid error message: ' + msg)
        self.assertTrue(msg.endswith('): exists, must be unique'),
                        'Invalid error message: ' + msg)

    def add_required_project_ids(self, project_json, required_sysid_list):
        project_ids = project_json.get('project_ids')
        system_list = set()
        for pid_json in project_ids:
            system_name = pid_json.get('system').get('system')
            system_list.add(system_name)
        for sys in required_sysid_list.difference(system_list):
            project_ids.append({
                "identifier": api_utils.get_random_string(12),
                "system": self.system_id_map.get(sys),
            })

    def validate_project_access(self):
        def fetch_project_by_request_param():
            view = ProjectViewSet.as_view({'get': 'list',
                                           'post': 'update'})

            url_with_param = 'api/project?request_id=' + str(request_id)
            request = self.factory.get(url_with_param,)
            request.user = self.user
            return view(request)

        project_json = self.generate_test_data_fn(self.user.id,
                                                  self.user_contact)
        response = self._create_project_common(project_json, True)
        project_id = response.data.get('id')
        request_id = response.data.get('requests')[0].get('id')

        # Access project as not contact and not approver
        # List access without URL param
        self.setup_new_user()
        response = self._get_project_data_by_id(project_id, False)
        msg = 'Access to project must be restricted to Project Contact'
        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, msg)

        # Detail access with URL param request_id
        role_list = roleUtils.ROLE_FB_MAP.keys()
        self.apply_fn_to_userrole_combo(role_list,
                                        fetch_project_by_request_param)


class NectarProjectTests(BaseProjectTests):
    def setUp(self):
        def test_data_fn(user_id, contact_obj, project_ids=None):
            return sampleData.get_base_nectar_project_data(user_id,
                                                           contact_obj,
                                                           project_ids)

        super().setUp(test_data_fn, 'NeCTAR')

    def test_project_id_prefix(self):
        required_ids_set = set([DBConstants.SYSTEM_NECTAR])
        project_json = self.generate_test_data_fn(self.user.id,
                                                  self.user_contact)
        super().validate_project_id_prefix(project_json, required_ids_set)

    def test_concurrent_project_update(self):
        super().validate_concurrent_project_update()

    def test_request_id_param_access(self):
        super().validate_project_access()

    def test_duplicate_project_id_fail(self):
        req_set = set([DBConstants.SYSTEM_NECTAR])
        super().validate_duplicate_project_id(req_set)

    def test_unique_project_identifier(self):
        required_ids_set = set([DBConstants.SYSTEM_NECTAR])
        project_json = self.generate_test_data_fn(self.user.id,
                                                  self.user_contact)
        self.add_required_project_ids(project_json, required_ids_set)
        project_ids = project_json.get('project_ids')
        self._create_project_common(project_json, True)

        # create another project with same nectar project id
        project_json = self.generate_test_data_fn(
            self.user.id, self.user_contact, project_ids)
        response = self._create_project_common(project_json, False)
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            'Unique Nectar project id constraint violation ')
        identifier = '???'
        for p_id in project_ids:
            if p_id['system']['system'] == DBConstants.SYSTEM_NECTAR:
                identifier = p_id['identifier']
        expected_msg = 'Project Id ({}): exists, must be unique'
        expected_msg = expected_msg.format(identifier)
        self.assertEqual(response.data.get('detail'),
                         expected_msg,
                         'Unique Nectar project id Error message do not match')
