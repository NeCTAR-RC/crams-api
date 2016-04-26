from rest_framework import status
from crams.models import Contact, CramsToken
from crams_api.tests.baseTest import CRAMSApiTstCase
from crams_api.tests.baseCramsFlow import _AbstractCramsBase
from crams_api.views import ProjectViewSet
from crams.dbUtils import get_request_status_lookups
from tests.sampleData import get_project_only_no_request_data
from tests.sampleData import get_base_nectar_project_data


__author__ = 'melvin luong, rafi m feroze'  # 'mmohamed'


class ProjectViewSetTest(CRAMSApiTstCase):
    fixtures = ['test_common_data']

    def test_project_fetch(self):
        view = ProjectViewSet.as_view({'get': 'list', 'post': 'create'})
        project_data = get_project_only_no_request_data(self.user.id,
                                                        self.contact)
        request = self.factory.post(
            'api/project',
            project_data,
            HTTP_AUTHORIZATION='Token {}'.format(
                self.token.key))

        response = view(request)

        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED, response.data)
        self.assertIsNot(response.data.get("id"), 0, response.data)
        self.assertEqual(response.data.get("title"),
                         project_data.get("title"), response.data)


class ProjectTests(_AbstractCramsBase):
    def setUp(self):
        _AbstractCramsBase.setUp(self)
        self.contact_email = 'newContact@monash.edu'
        self.contact, created = Contact.objects.get_or_create(
            title='Mr', given_name='Test', surname='MeRC',
            email=self.contact_email,
            phone='99020780', organisation='Monash University')

        self.test_data = get_base_nectar_project_data(self.user.id,
                                                      self.contact)
        self.provisioner_name = 'NeCTAR'
        self.requestStatusLookups = get_request_status_lookups()

    def test_concurrent_project_update(self):
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
        self.test_data = get_base_nectar_project_data(self.user.id,
                                                      self.contact)

        response = self.createNew()
        originalUser = self.user
        originalToken = self.token

        self.user = contact_user
        self.token = contact_token
        self.updateSomething(response)

        self.user = originalUser
        self.token = originalToken
        self._updateResponseDataRandom(response.data, _updateFailFn)
