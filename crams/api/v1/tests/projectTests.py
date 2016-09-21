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


class ProjectViewSetTest(CRAMSApiTstCase):
    fixtures = ['v1/test_common_data']

    def test_project_fetch(self):
        view = ProjectViewSet.as_view({'get': 'list', 'post': 'create'})
        project_data = get_project_only_no_request_data(self.user.id,
                                                        self.contact)
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
        self.contact, created = Contact.objects.get_or_create(
            title='Mr', given_name='Test', surname='MeRC',
            email=self.contact_email,
            phone='99020780', organisation='Monash University')

        self.generate_test_data_fn = test_data_fn
        self.test_data = self.generate_test_data_fn(self.user.id, self.contact)

        self.provisioner_name = provisioner_name
        self.requestStatusLookups = dbUtils.get_request_status_lookups()
        self.system_id_map = dbUtils.get_system_name_map()

    def validate_concurrent_project_update(self):
        def _updateFailFn(response):
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                'concurrent update should fail : {}'.format(
                    response.data))
            expected_msg = 'concurrent update: <User: newContact@monash.edu>' \
                           ' has updated project, please refresh and try again'
            self.assertEqual(response.data.get('non_field_errors')[0],
                             expected_msg,
                             'Concurrent Error messages do not match')

        contact_user = self._getUser('randomUser', self.contact_email)
        contact_token, created = CramsToken.objects.get_or_create(
            user=contact_user)
        self.test_data = self.generate_test_data_fn(self.user.id, self.contact)

        response = self.createNew()
        originalUser = self.user
        originalToken = self.token

        self.user = contact_user
        self.token = contact_token
        self.updateSomething(response)

        self.user = originalUser
        self.token = originalToken
        self._updateResponseDataRandom(response.data, _updateFailFn)

    def validate_project_id_prefix(self, project_json,
                                   required_sysid_list=set()):
        # ensure project data has project_ids from required_sysid_list
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

        pid_map = settings.PROJECT_SYSTEM_ID_INVALID_PREFIX_MAP
        for pid_json in project_json.get('project_ids'):
            system_name = pid_json.get('system').get('system').lower()
            if system_name in pid_map.keys():
                invalid_prefix_list = pid_map.get(system_name)
                if not invalid_prefix_list:
                    continue
                all_combo_invalid_list = list()
                for base_prefix in invalid_prefix_list:
                    all_combo_invalid_list.extend(
                        api_utils.generate_all_case_combinations(base_prefix))
                for invalid_prefix in all_combo_invalid_list:
                    s_id = invalid_prefix + pid_json.get('identifier')
                    pid_json['identifier'] = s_id
                    response = self._create_project_common(project_json, False)
                    msg = 'sys id cannot begin with: {}'.format(invalid_prefix)
                    self.assertEqual(response.status_code,
                                     status.HTTP_400_BAD_REQUEST,
                                     msg)


class NectarProjectTests(BaseProjectTests):
    def setUp(self):
        def test_data_fn(user_id, contact_obj):
            return sampleData.get_base_nectar_project_data(user_id,
                                                           contact_obj)

        super().setUp(test_data_fn, 'NeCTAR')

    def test_project_id_prefix(self):
        required_ids_set = set([DBConstants.SYSTEM_NECTAR])
        project_json = self.generate_test_data_fn(self.user.id, self.contact)
        super().validate_project_id_prefix(project_json, required_ids_set)

    def test_concurrent_project_update(self):
        super().validate_concurrent_project_update()
