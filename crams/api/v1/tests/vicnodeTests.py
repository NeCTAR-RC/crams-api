from rest_framework import status

from crams.models import Project
from tests.sampleData import get_vicnode_test_data
from crams.api.v1.tests.baseTest import CRAMSApiTstCase
from crams.api.v1.views import ProjectViewSet

__author__ = 'melvin luong, rafi m feroze'  # 'mmohamed'


class VicNodeProjectViewSetTest(CRAMSApiTstCase):
    fixtures = ['v1/test_common_data', 'v1/test_vicnode_data']

    def setUp(self):
        CRAMSApiTstCase.setUp(self)
        # override the user and token in the fixtures with test_data
        # self.user = User.objects.get(username="crams_user")
        # self.token = Token.objects.get_or_create(user=self.user)[0]

        self.test_data = get_vicnode_test_data(self.user.id, self.contact)

    def test_request_creation(self):
        self._create_project_common(self.test_data)

    def test_request_update(self):
        # creating request
        response = self._create_project_common(self.test_data)

        # get project and request id
        project1 = response.data
        request1 = response.data.get("requests")[0]

        # update storage request 1st changes
        quota = 1200
        approved_quota = 1200
        request1["storage_requests"][0]["quota"] = quota
        request1["storage_requests"][0]["approved_quota"] = approved_quota

        # 1st update
        response = self._update_vicproject_common(
            project1, request1['id'], quota, approved_quota)

        # get new project and request id
        project2 = response.data
        self.assertIsNotNone(
            project2.get(
                'id',
                None),
            'Project id is None after update 1. ' +
            repr(
                response.data))
        request2 = response.data.get("requests")[0]

        # update storage request 2nd changes
        quota = 1000
        approved_quota = 1000
        request2["storage_requests"][0]["quota"] = quota
        request2["storage_requests"][0]["approved_quota"] = approved_quota

        # 2nd update
        response = self._update_vicproject_common(
            project2, request2['id'], quota, approved_quota)

        # get new project and request id
        project3 = response.data
        self.assertIsNotNone(
            project3.get(
                'id',
                None),
            'Project id is None after update 2. ' +
            repr(
                response.data))
        request3 = response.data.get("requests")[0]

        # update storage request 3rd changes
        quota = 800
        approved_quota = 800
        request3["storage_requests"][0]["quota"] = quota
        request3["storage_requests"][0]["approved_quota"] = approved_quota

        # 3rd update
        response = self._update_vicproject_common(
            project3, request3['id'], quota, approved_quota)

        # get new project id
        project_4_id = response.data.get("id")
        self.assertIsNotNone(
            project_4_id,
            'Project id is None after update 3. ' +
            repr(
                response.data))

        projects = Project.objects.filter(parent_project_id=project_4_id)
        self.assertEqual(len(projects), 3, response.data)

    def test_request_update_history_fail(self):
        def _updateFailFn(response):
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                             'update history fail : {}'.format(response.data))

        # creating request
        response = self._create_project_common(self.test_data)

        # get project id
        response.data.get("id")
        request_id = response.data.get("requests")[0]["id"]

        # modify test_data
        test_data = response.data

        # update storage
        test_data["requests"][0]["storage_requests"][0]["quota"] = 4000
        test_data["requests"][0]["storage_requests"][
            0]["approved_quota"] = 4000

        # update project/request first time
        self._update_vicproject_common(test_data, request_id, 4000, 4000)
        # update the same project/request again
        self._update_vicproject_common(
            test_data, request_id, 4000, 4000, _updateFailFn)

    def test_request_get(self):
        # create atleast one project/request for testing get
        self._create_project_common(self.test_data)
        atleastOneProjectRequestExists = False
        view = ProjectViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get(
            'api/project',
            HTTP_AUTHORIZATION='Token {}'.format(
                self.token.key))
        for p in Project.objects.filter(project_ids__system__system='VicNode',
                                        requests__isnull=False,
                                        parent_project__isnull=True):
            response = view(request, pk=str(p.id))
            if response.status_code == status.HTTP_403_FORBIDDEN:
                continue  # Ignore rows for which user is not authorized
            # Expecting HTTP 200 response status
            self.assertEqual(response.status_code,
                             status.HTTP_200_OK, response.data)
            projectData = response.data
            self.assertEqual(projectData.get('id', None), p.id, response.data)
            self.assertEqual(projectData.get('title', None),
                             p.title, response.data)
            requestIdList = set()
            for requestData in projectData.get('requests', None):
                requestIdList.add(requestData['id'])
            if len(requestIdList) > 0:
                atleastOneProjectRequestExists = True
            for r in p.requests.all():
                if r.parent_request:
                    self.assertFalse(
                        r.id in requestIdList,
                        'Archived Request should not be returned by API - '
                        'project {} /request {}'.format(p.id, r.id))
                else:
                    self.assertTrue(
                        r.id in requestIdList,
                        'Request not fetched for project {} /request {}'.
                        format(p.id, r.id))

        self.assertTrue(atleastOneProjectRequestExists,
                        'Error, no project with request exists for testing')

    def test_request_get_by_request_id(self):
        # get the request from the first project where request status is
        # "Approved" for tests
        view = ProjectViewSet.as_view({'get': 'list'})
        for p in Project.objects.filter(project_ids__system__system='VicNode',
                                        requests__isnull=False,
                                        parent_project__isnull=True):
            for r in p.requests.filter(parent_request__isnull=True):
                request = self.factory.get(
                    'api/project/' + str(p.id) + '/?request_id=' + str(r.id),
                    HTTP_AUTHORIZATION='Token {}'.format(self.token.key))
                response = view(request)
                if response.status_code == status.HTTP_403_FORBIDDEN:
                    continue  # Ignore rows for which user is not authorized

                # else Expecting HTTP 200 response status
                self.assertEqual(response.status_code,
                                 status.HTTP_200_OK, response.data)
                # Expecting project id
                # List view return an array, even though the API is for a
                # specific project request
                projectData = response.data[0]

                self.assertEqual(projectData.get(
                    'id', None), p.id, projectData)
                # Expecting current request as first and only object in
                # requestArray
                requestArray = projectData.get('requests', [])
                self.assertTrue(len(requestArray) == 1)
                request = requestArray[0]
                self.assertEqual(request.get('id', None), r.id, response.data)

    def _update_vicproject_common(
            self,
            test_data,
            request_id,
            quota,
            approved_quota,
            updateValidateFn=None):
        def _updateSuccessFn(response):
            # get the new updated id's
            new_project_id = response.data.get("id")

            # check HTTP 200
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                'update project fail for project_id {} : {}'.format(
                    repr(
                        test_data['id']),
                    repr(
                        response.data)))
            # check new project and requests is created with new id
            self.assertNotEqual(new_project_id, test_data['id'], response.data)

            self.assertGreater(
                len(response.data.get("requests")), 0, response.data)
            new_request_id = response.data.get("requests")[0]["id"]
            self.assertNotEqual(new_request_id, request_id, response.data)
            # check requests has changed
            self.assertEqual(response.data.get(
                "requests")[0]["storage_requests"][0]["quota"],
                quota, response.data)
            self.assertEqual(
                response.data.get(
                    "requests")[0]["storage_requests"][0]["approved_quota"],
                approved_quota, response.data)

            return response

        view = ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update'})
        request = self.factory.put(
            '', test_data, HTTP_AUTHORIZATION='Token {}'.format(
                self.token.key))
        request.user = self.user
        response = view(request, pk=test_data['id'])

        if updateValidateFn:
            return updateValidateFn(response)
        else:
            return _updateSuccessFn(response)
