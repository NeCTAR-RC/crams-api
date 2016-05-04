from django.forms import model_to_dict
from rest_framework import status

from crams.models import Contact
from api.v1.tests.baseTest import CRAMSApiTstCase
from api.v1.views import ContactViewSet, SearchContact

__author__ = 'melvin luong, rafi m feroze'  # 'mmohamed'


class ContactTest(CRAMSApiTstCase):

    def setUp(self):
        CRAMSApiTstCase.setUp(self)
        self.search_contact_1 = Contact.objects.create(
            title='Mr',
            given_name='John',
            surname='Smith',
            email='john.smith@monash.edu',
            phone='0399020780',
            organisation='Monash University')
        self.search_contact_2 = Contact.objects.create(
            title='Mr',
            given_name='John',
            surname='Doe',
            email='john.doe@monash.edu',
            phone='0399020780',
            organisation='Monash University')
        self.search_contact_3 = Contact.objects.create(
            title='Mr',
            given_name='Jane',
            surname='Doe',
            email='jane.doe@monash.edu',
            phone='0399020780',
            organisation='Monash University')

    # Test Rest POST for Contact
    def test_contact_create(self):
        test_data = {
            "title": "Mr.",
            "given_name": "Test",
            "surname": "Test",
            "email": "tests@email.com",
            "phone": "123456789",
            "organisation": "Monash"
        }

        view = ContactViewSet.as_view({'get': 'retrieve', 'post': 'create'})
        # POST create new contact using tests data
        request = self.factory.post('api/contact', test_data)
        request.user = self.user
        response = view(request)

        # HTTP 201
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data)
        # remove the 'id' element from results to match the tests data json
        del response.data['id']
        # Results match tests data
        self.assertEqual(response.data, test_data, response.data)

    # Test Rest GET for Contact
    def test_contact_get(self):
        # contact to retrieve from GET
        contact = Contact.objects.get(email="john.smith@monash.edu")

        view = ContactViewSet.as_view({'get': 'retrieve'})
        # GET contact using contact.id
        request = self.factory.get('api/contact')
        request.user = self.user
        response = view(request, pk=contact.id)

        # HTTP 200
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data)
        # Results match tests data
        self.assertEqual(response.data, model_to_dict(contact), response.data)

    # Test Rest PUT for Contact
    def test_contact_put(self):
        contact = Contact.objects.get(email="tests.merc@monash.edu")

        test_data = {
            "id": contact.id,
            "title": "Mr",
            "given_name": "Test",
            "surname": "MeRC",
            "email": "tests.merc@gmail.com",
            "phone": "123456789",
            "organisation": "Google"
        }

        view = ContactViewSet.as_view({'get': 'retrieve', 'put': 'update'})
        # update contact
        request = self.factory.put('api/contact', test_data)
        request.user = self.user
        response = view(request, pk=contact.id)

        # HTTP 200
        self.assertEquals(
            response.status_code,
            status.HTTP_200_OK,
            response.data)
        # Results match tests data
        self.assertEquals(response.data, test_data, response.data)

    # Test Rest PATCH for Contact
    def test_contact_patch(self):
        contact = Contact.objects.get(email="tests.merc@monash.edu")

        view = ContactViewSet.as_view(
            {'get': 'retrieve', 'patch': 'partial_update'})
        # update email
        request = self.factory.patch(
            'api/contact', {"email": "tests.merc@hotmail.com"})
        request.user = self.user
        response = view(request, pk=contact.id)

        # HTTP 200
        self.assertEquals(
            response.status_code,
            status.HTTP_200_OK,
            response.data)
        # Email has been updated
        self.assertEquals(
            response.data.get("email"),
            'tests.merc@hotmail.com',
            response.data)

    # Test email validation for POST contact
    def test_contact_post_email_validation(self):
        test_data = {
            "id": 5,
            "title": "Mr.",
            "given_name": "Test",
            "surname": "Test",
            "email": "tests.merc@monash.edu",  # existing email from setUp
            "phone": "123456789",
            "organisation": "Monash"
        }

        view = ContactViewSet.as_view({'get': 'retrieve', 'post': 'create'})
        # POST create new contact using tests data
        request = self.factory.post('api/contact', test_data)
        request.user = self.user
        response = view(request)

        # HTTP 400
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data)
        # Expected error message
        self.assertEqual(str(response.data.get('email')[
                         0]), 'This field must be unique.', response.data)

    # Test email validation for PUT contact
    def test_contact_put_email_validation(self):
        contact = Contact.objects.get(email="tests.merc@monash.edu")

        test_data = {
            "id": contact.id,
            "title": "Mr",
            "given_name": "Test",
            "surname": "MeRC",
            "email": "john.smith@monash.edu",  # existing email from setUp
            "phone": "123456789",
            "organisation": "Google"
        }

        view = ContactViewSet.as_view({'get': 'retrieve', 'put': 'update'})
        # update contact
        request = self.factory.put('api/contact', test_data)
        request.user = self.user
        response = view(request, pk=contact.id)

        # HTTP 400
        self.assertEquals(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data)
        # Expected error message
        self.assertEqual(str(response.data.get('email')[
                         0]), 'This field must be unique.', response.data)

    # Test email validation for PATCH contact
    def test_contact_patch_validation(self):
        contact = Contact.objects.get(email="tests.merc@monash.edu")

        view = ContactViewSet.as_view(
            {'get': 'retrieve', 'patch': 'partial_update'})
        # update email with an existing email
        request = self.factory.patch(
            'api/contact', {'email': 'john.smith@monash.edu'})
        request.user = self.user
        response = view(request, pk=contact.id)

        # HTTP 400
        self.assertEquals(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data)
        # Expected error message
        self.assertEquals(str(response.data.get("email")[
                          0]), 'This field must be unique.', response.data)

    # Test search function, searching using given_name
    def test_contact_search_given_name(self):
        john_smith_contact = Contact.objects.get(email='john.smith@monash.edu')
        john_doe_contact = Contact.objects.get(email='john.doe@monash.edu')

        view = SearchContact.as_view()
        # search for given_name john
        request = self.factory.get('api/searchcontact?search=john')
        request.user = self.user
        response = view(request)
        john_smith = self._convert_to_valid_search_dict(john_smith_contact)
        john_doe = self._convert_to_valid_search_dict(john_doe_contact)

        # HTTP 200
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data)
        # Returns 2 results
        self.assertEquals(len(response.data), 2, response.data)
        # Results contains john smith contact
        self.assertTrue(john_smith in response.data, response.data)
        # Results contain john doe
        self.assertTrue(john_doe in response.data, response.data)

    # Test search function, searching using surname
    def test_contact_search_surname(self):
        john_doe_contact = Contact.objects.get(email='john.doe@monash.edu')
        jane_doe_contact = Contact.objects.get(email='jane.doe@monash.edu')

        view = SearchContact.as_view()
        # search for surname doe
        request = self.factory.get('api/searchcontact?search=doe')
        request.user = self.user
        response = view(request)
        john_doe = self._convert_to_valid_search_dict(john_doe_contact)
        jane_doe = self._convert_to_valid_search_dict(jane_doe_contact)

        # HTTP 200
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data)
        # Returns 2 results
        self.assertEquals(len(response.data), 2, response.data)
        # Results contain jane doe contact
        self.assertTrue(jane_doe in response.data, response.data)
        # Results contain john doe contact
        self.assertTrue(john_doe in response.data, response.data)

    # Test search function, searching using email
    def test_contact_search_email(self):
        search_email = 'john.smith@monash.edu'
        contact = Contact.objects.get(email=search_email)

        view = SearchContact.as_view()
        # search for email john.smith@monash.edu
        request = self.factory.get('api/searchcontact?search=' + search_email)
        request.user = self.user
        response = view(request)
        john_smith = self._convert_to_valid_search_dict(contact)

        # HTTP 200
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data)
        # Returns 1 result
        self.assertEquals(len(response.data), 1, response.data)
        # Results match tests data
        self.assertEquals(dict(response.data[0]), john_smith, response.data)

    # Test contact get auth access
    def test_contact_get_auth(self):
        view = ContactViewSet.as_view({'get': 'retrieve'})
        # GET contact where id == 1
        request = self.factory.get('api/contact/1')

        response = view(request)

        # HTTP 401
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            response.data)

    # Test contact list auth access
    def test_contact_list_auth(self):
        view = ContactViewSet.as_view({'get': 'list'})
        # GET contact where id == 1
        request = self.factory.get('api/contact')

        response = view(request)

        # HTTP 401
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            response.data)

    # Test contact search auth access
    def test_contact_search_auth(self):
        view = SearchContact.as_view()
        request = self.factory.get('api/searchcontact?search=john')

        response = view(request)

        # HTTP 401
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            response.data)

    def test_contact_patch_auth(self):
        view = ContactViewSet.as_view(
            {'get': 'retrieve', 'patch': 'partial_update'})
        # update email with an existing email
        request = self.factory.patch(
            'api/contact/1', {'email': 'new_email_addr@monash.edu'})
        response = view(request, pk="1")

        # HTTP 401
        self.assertEquals(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            response.data)

    def test_contact_put_auth(self):
        test_data = {
            "id": 1,
            "title": "Mr",
            "given_name": "Test",
            "surname": "MeRC",
            "email": "tests.merc@gmail.com",
            "phone": "123456789",
            "organisation": "Google"
        }

        view = ContactViewSet.as_view({'get': 'retrieve', 'put': 'update'})
        # update contact where id == 1 with test_data
        request = self.factory.put('api/contact/1', test_data)
        response = view(request, pk="1")

        # HTTP 401
        self.assertEquals(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            response.data)

    def test_contact_post_auth(self):
        test_data = {
            "id": 5,
            "title": "Mr.",
            "given_name": "Test",
            "surname": "Test",
            "email": "tests.merc@monash.edu",  # existing email from setUp
            "phone": "123456789",
            "organisation": "Monash"
        }

        view = ContactViewSet.as_view({'get': 'retrieve', 'post': 'create'})
        # POST create new contact using tests data
        request = self.factory.post('api/contact', test_data)
        response = view(request)

        # HTTP 401
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            response.data)

    def test_contact_create_auth(self):
        test_data = {
            "id": 5,
            "title": "Mr.",
            "given_name": "Test",
            "surname": "Test",
            "email": "tests@email.com",
            "phone": "123456789",
            "organisation": "Monash"
        }

        view = ContactViewSet.as_view({'get': 'retrieve', 'post': 'create'})
        # POST create new contact using tests data
        request = self.factory.post('api/contact', test_data)
        response = view(request)

        # HTTP 401
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            response.data)

    # Converts contact to dict and removes the sensitive fields
    def _convert_to_valid_search_dict(self, contact):
        d = model_to_dict(contact)
        del d['phone']
        del d['organisation']
        return d
