from rest_framework import status

from crams.models import Project, Request
from tests.sampleData import get_base_nectar_project_data
from crams.api.v1.tests.baseTest import CRAMSApiTstCase
from crams.api.v1.views import ProjectViewSet, RequestViewSet
from crams import roleUtils
from tests import sampleData


class CramsProjectViewSetTest(CRAMSApiTstCase):
    fixtures = ['v1/test_common_data', 'v1/test_nectar_data']

    def setUp(self):
        CRAMSApiTstCase.setUp(self)
        self.test_data = get_base_nectar_project_data(self.user.id,
                                                      self.user_contact)

    def test_request_creation(self):
        self._create_project_common(self.test_data)

    def test_request_update(self):
        def _updateProductRequest(
                projectDict,
                requestDict,
                instances,
                cores,
                quota,
                assert_response=True):
            # update compute
            compute_requests = requestDict.get('compute_requests', [])
            if compute_requests:
                requestDict["compute_requests"][0]["instances"] = instances
                requestDict["compute_requests"][0]["cores"] = cores
            # update storage
            storage_requests = requestDict.get('storage_requests', [])
            if storage_requests:
                requestDict["storage_requests"][0]["quota"] = quota

            # update request
            response = self._update_project_common(
                projectDict, requestDict.get('id'), instances, cores, quota)

            if assert_response:
                self.assertEqual(response.status_code,
                                 status.HTTP_200_OK,
                                 'update fail : {}'.format(response.data))
                requests = response.data.get('requests')
                err_msg = 'Expected one request, got None'
                self.assertIsNotNone(requests, err_msg)
                err_msg = 'Expected one request, got {} requests'.format(
                    str(len(requests))
                )
                self.assertEqual(len(requests), 1, err_msg)

                storage_requests = requests[0].get('storage_requests')
                err_msg = 'Expected storage requests, got None'
                self.assertIsNotNone(storage_requests, err_msg)
                err_msg = 'Expected 1 storage request, got {}'.format(
                    str(len(storage_requests)))
                self.assertEqual(len(storage_requests), 1, err_msg)
                storage_request = storage_requests[0]
                self.assertEqual(storage_request.get('quota'), quota)

                compute_requests = requests[0].get('compute_requests')
                err_msg = 'Expected compute requests, got None'
                self.assertIsNotNone(compute_requests, err_msg)
                err_msg = 'Expected 1 compute request, got {}'.format(
                    str(len(compute_requests)))
                self.assertEqual(len(compute_requests), 1, err_msg)
                compute_request = compute_requests[0]
                self.assertEqual(compute_request.get('instances'), instances)
                self.assertEqual(compute_request.get('cores'), cores)

            return response
        # creating request
        response = self._create_project_common(self.test_data)

        # get project id
        project1 = response.data
        request1 = project1.get("requests")[0]

        # 1st update
        instances = 4
        cores = 4
        quota = 4000
        response = _updateProductRequest(
            project1, request1, instances, cores, quota)

        # get new project and request id
        project2 = response.data
        request2 = project2.get("requests")[0]

        # 2nd update
        instances = 8
        cores = 8
        quota = 8000
        response = _updateProductRequest(
            project2, request2, instances, cores, quota)

        # get new request id
        project3 = response.data
        request3 = project3.get("requests")[0]

        # 3rd update
        instances = 12
        cores = 12
        quota = 12000
        response = _updateProductRequest(
            project3, request3, instances, cores, quota)

        # get new request id
        project4 = response.data

        # check project history
        projects = Project.objects.filter(parent_project_id=project4.get('id'))
        self.assertEqual(len(projects), 3, response.data)

    def test_request_update_history_fail(self):
        def _updateFailFn(response):
            # The Viewset will not fetch history records without param
            # request_id
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                             'update history fail : {}'.format(response.data))

        # creating request
        response = self._create_project_common(self.test_data)

        # get project id
        project = response.data
        requestData = response.data.get("requests")[0]

        # modify test_data
        # update compute
        instances = 4
        cores = 4
        quota = 4000
        compute_requests = requestData.get('compute_requests', [])
        if compute_requests:
            requestData["compute_requests"][0]["instances"] = instances
            requestData["compute_requests"][0]["cores"] = cores
        # update storage
        storage_requests = requestData.get('storage_requests', [])
        if storage_requests:
            requestData["storage_requests"][0]["quota"] = quota

        # update project/request first time
        self._update_project_common(
            project, requestData.get('id'), instances, cores, quota)
        # update the same project/request again
        self._update_project_common(project, requestData.get(
            'id'), instances, cores, quota, _updateFailFn)

    def test_request_get(self):
        # create atleast one project/request for testing get
        self._create_project_common(self.test_data)

        atleastOneProjectRequestExists = False
        view = ProjectViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get('api/project')
        request.user = self.user

        for p in Project.objects.filter(
                requests__isnull=False,
                parent_project__isnull=True):
            response = view(request, pk=str(p.id))
            if response.status_code == status.HTTP_404_NOT_FOUND:
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
                        'Historic Request should not be returned by API - '
                        'project {} /request {}'.format(p.id, r.id))
                else:
                    self.assertTrue(
                        r.id in requestIdList,
                        'Request not fetched for project {} / request {}'.
                        format(p.id, r.id))

        self.assertTrue(atleastOneProjectRequestExists,
                        'Error, no project with request exists for testing')

    def test_request_get_by_request_id(self):
        # get the request from the first project where request status is
        # "Approved" for tests
        view = ProjectViewSet.as_view({'get': 'list'})
        for p in Project.objects.filter(
                requests__isnull=False,
                parent_project__isnull=True):
            for r in p.requests.filter(parent_request__isnull=True):
                request = self.factory.get(
                    'api/project/' + str(p.id) + '/?request_id=' + str(r.id))
                request.user = self.user

                response = view(request)
                if response.status_code == status.HTTP_403_FORBIDDEN:
                    continue  # Ignore rows for which user is not authorized

                # else Expecting HTTP 200 response status
                self.assertEqual(response.status_code,
                                 status.HTTP_200_OK, response.data)
                # Expecting project id
                # List view return an array, even though the API is for a
                # specific project request
                if not response.data:  # could be empty list
                    return

                projectData = response.data[0]

                self.assertEqual(projectData.get(
                    'id', None), p.id, projectData)
                # Expecting current request as first and only object in
                # requestArray
                requestArray = projectData.get('requests', [])
                self.assertTrue(len(requestArray) == 1)
                request = requestArray[0]
                self.assertEqual(request.get('id', None), r.id, response.data)


class RequestViewSetTest(CRAMSApiTstCase):
    fixtures = ['v1/test_common_data', 'v1/test_nectar_data']

    def setUp(self, test_data_fn):
        CRAMSApiTstCase.setUp(self)
        self.generate_test_data_fn = test_data_fn
        self.test_data = self.generate_test_data_fn(self.user.id,
                                                    self.user_contact)

    def get_request_data_by_id(self, request_id, validate_response=True):
        view = RequestViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get('api/request')
        request.user = self.user
        response = view(request, pk=str(request_id))
        if validate_response:
            # Expecting HTTP 200 response status
            self.assertEqual(response.status_code,
                             status.HTTP_200_OK, response.data)
        return response

    def validate_request_id_param_access(self):
        def fetch_request_by_request_param():
            view = RequestViewSet.as_view({'get': 'list',
                                           'post': 'update'})

            url_with_param = 'api/request?request_id=' + str(request_id)
            request = self.factory.get(url_with_param,)
            request.user = self.user
            return view(request)

        project_json = self.generate_test_data_fn(self.user.id,
                                                  self.user_contact)
        response = self._create_project_common(project_json, True)
        request_id = response.data.get('id')

        # Access project as not contact and not approver
        # List access without URL param
        self.setup_new_user()
        response = self.get_request_data_by_id(request_id, False)
        msg = 'Access to request must be restricted to Project Contact'
        status_code = response.status_code
        self.assertEqual(status_code, status.HTTP_403_FORBIDDEN, msg)

        # Detail access with URL param request_id
        role_list = roleUtils.ROLE_FB_MAP.keys()
        self.apply_fn_to_userrole_combo(role_list,
                                        fetch_request_by_request_param)

    # Test Rest GET for Request
    def validate_request_list_get(self):
        # create atleast one project/request for testing get
        self._create_project_common(self.test_data)

        view = RequestViewSet.as_view({'get': 'retrieve'})
        # GET request
        request = self.factory.get('api/request')
        request.user = self.user

        # get the first request from tests data set
        projects = self.user_contact.project_contacts.distinct().\
            values_list('project', flat=True)
        request_obj = Request.objects.filter(project__in=projects).first()
        self.assertIsNotNone(request_obj, 'No Requests found in DB')
        response = view(request, pk=request_obj.id)

        # HTTP 200
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, response.data)
        # Results request match tests data
        self.assertEqual(response.data['id'], request_obj.id, response.data)
        self.assertEqual(response.data['project'],
                         request_obj.project.id, response.data)
        self.assertEqual(
            response.data['request_status']['code'],
            request_obj.request_status.code,
            response.data)


class NectarRequestTests(RequestViewSetTest):
    def setUp(self):
        def test_data_fn(user_id, contact_obj, project_ids=None):
            return sampleData.get_base_nectar_project_data(user_id,
                                                           contact_obj,
                                                           project_ids)

        super().setUp(test_data_fn, 'NeCTAR')

    def validate_request_id_param_access(self):
        super().validate_request_id_param_access()

    def validate_request_list_get(self):
        super().validate_request_list_get()
