# coding=utf-8
"""List Serializers."""

from crams.api.v1.serializers.lookupSerializers import ComputeProductSerializer
from crams.api.v1.serializers.lookupSerializers import QuestionSerializer
from crams.api.v1.serializers.lookupSerializers import StorageProductSerializer
from crams.api.v1.serializers.projectSerializers import ContactSerializer
from crams.api.v1.serializers.projectSerializers import DomainSerializer
from crams.api.v1.serializers.projectSerializers import GrantSerializer
from crams.api.v1.serializers.projectSerializers import ProjectContactSerializer
from crams.api.v1.serializers.projectSerializers import ProjectIDSerializer
from crams.api.v1.serializers.projectSerializers import \
    ProjectQuestionResponseSerializer
from crams.api.v1.serializers.projectSerializers import ProjectSerializer
from crams.api.v1.serializers.projectSerializers import PublicationSerializer
from crams.api.v1.serializers.projectSerializers import \
    SupportedInstitutionSerializer
from crams.api.v1.serializers.requestSerializers import ComputeRequestSerializer
from crams.api.v1.serializers.requestSerializers import CramsRequestSerializer
from crams.api.v1.serializers.requestSerializers import \
    RequestQuestionResponseSerializer
from crams.api.v1.serializers.requestSerializers import StorageRequestSerializer
from crams.api.v1.serializers.utilitySerializers import \
    DynamicFieldsBaseSerializer

__author__ = 'rafi m feroze'


# noinspection PyUnusedLocal
class ListAPIMixin(object):
    """class ListAPIMixin."""

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return:
        """
        return self.instance

    def update(self, instance, validated_data):
        """udate.

        :param instance:
        :param validated_data:
        :return:
        """
        return instance


class GrantListSerializer(GrantSerializer, ListAPIMixin):
    """class GrantListSerializer."""

    grant_type = DynamicFieldsBaseSerializer(display=('id', 'description'))


class PublicationListSerializer(PublicationSerializer, ListAPIMixin):
    """class PublicationListSerializer."""

    pass


class SupportedInstitutionListSerializer(
        SupportedInstitutionSerializer, ListAPIMixin):
    """class PublicationListSerializer."""

    pass


class ProjectQuestionResponseListSerializer(
        ProjectQuestionResponseSerializer, ListAPIMixin):
    """class ProjectQuestionResponseListSerializer."""

    pass


class DomainListSerializer(DomainSerializer, ListAPIMixin):
    """class DomainListSerializer."""

    for_code = DynamicFieldsBaseSerializer(display=('id', 'code'))


class ProjectIDListSerializer(ProjectIDSerializer, ListAPIMixin):
    """class ProjectIDListSerializer."""

    system = DynamicFieldsBaseSerializer(display=('id', 'system'))


class ContactListSerializer(ContactSerializer, ListAPIMixin):
    """class ContactListSerializer."""

    pass


class ProjectContactListSerializer(ProjectContactSerializer, ListAPIMixin):
    """class ProjectContactListSerializer."""

    contact = ContactListSerializer(many=True)
    contact_role = DynamicFieldsBaseSerializer(display=('id', 'name'))


class ProjectListSerializer(ProjectSerializer, ListAPIMixin):
    """class ProjectListSerializer."""

    # project question response
    project_question_responses = ProjectQuestionResponseListSerializer(
        many=True)

    # Supported institutions
    institutions = SupportedInstitutionListSerializer(many=True)

    # Publication
    publications = PublicationListSerializer(many=True)

    # Grant information
    grants = GrantListSerializer(many=True)

    # ProjectID
    project_ids = ProjectIDListSerializer(many=True)

    # Contacts
    project_contacts = ProjectContactListSerializer(many=True)

    # Domains
    domains = DomainListSerializer(many=True)


class ComputeProductListSerializer(ComputeProductSerializer, ListAPIMixin):
    """class ComputeProductListSerializer."""

    pass


class ComputeRequestListSerializer(ComputeRequestSerializer, ListAPIMixin):
    """class ComputeRequestListSerializer."""

    compute_product = ComputeProductListSerializer(many=False)


class StorageProductListSerializer(StorageProductSerializer, ListAPIMixin):
    """class StorageProductListSerializer."""

    pass


class StorageRequestListSerializer(StorageRequestSerializer, ListAPIMixin):
    """class StorageRequestListSerializer."""

    storage_product = StorageProductListSerializer(many=False)


class QuestionListSerializer(QuestionSerializer, ListAPIMixin):
    """class QuestionListSerializer."""

    pass


class RequestQuestionResponseListSerializer(
        RequestQuestionResponseSerializer, ListAPIMixin):
    """class RequestQuestionResponseListSerializer."""

    question = QuestionListSerializer(many=False)


class CramsRequestListSerializer(CramsRequestSerializer, ListAPIMixin):
    """class CramsRequestListSerializer."""

    project = ProjectListSerializer(many=False)

    compute_requests = ComputeRequestListSerializer(many=True)

    storage_requests = StorageRequestListSerializer(many=True)

    request_question_responses = RequestQuestionResponseListSerializer(
        many=True)
