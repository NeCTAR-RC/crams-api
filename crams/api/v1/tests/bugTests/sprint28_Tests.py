from crams.models import Contact
from tests.sampleData import get_base_nectar_project_data
from crams.api.v1.tests.baseTest import CRAMSApiTstCase
from crams.api.v1.utils import get_random_string


class Bug_719_TestCase(CRAMSApiTstCase):

    def setUp(self):
        CRAMSApiTstCase.setUp(self)
        self.test_data = get_base_nectar_project_data(self.user.id,
                                                      self.user_contact)

    def test_applicant_contact_should_not_fail_when_user_email_not_found(
            self):
        # change user email to some new random value
        self.user.email = get_random_string(
            7) + '@bug719.eresearchtest.monash.edu'
        self.user.save()
        for pc in self.test_data.get('project_contacts', []):
            contact = pc.get('contact', None)
            if contact:
                self.assertNotEqual(self.user.email, pc.get(contact.get(
                    'email', None)), 'Random email matches contact email')

        try:
            contactObj = Contact.objects.get(email=self.user.email)
            self.assertIsNone(
                contactObj,
                'Random Contact should not exist for email id ' +
                self.user.email)
        except Contact.DoesNotExist:
            pass
        except Contact.MultipleContactExists:
            self.assertIsNotNone(
                None,
                'Multiple contact exists with random email id ' +
                self.user.email)

        # Create should complete successfully
        self._create_project_common(self.test_data)
