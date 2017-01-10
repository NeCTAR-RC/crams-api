# coding=utf-8
"""Project Serailizers."""

from crams.api.v1.dataUtils.lookupData import LookupDataModel
from crams.api.v1.dataUtils.lookupData import get_system_obj
from crams.api.v1.serializers import requestSerializers
from crams.api.v1.serializers import utilitySerializers
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from crams.DBConstants import APPLICANT
from crams.DBConstants import SYSTEM_NECTAR
from crams.DBConstants import REQUEST_STATUS_APPROVED
from crams.api.v1.validators import projectid_validators
from crams.models import Contact
from crams.models import ContactRole
from crams.models import Domain
from crams.models import FORCode
from crams.models import Grant
from crams.models import GrantType
from crams.models import Project
from crams.models import ProjectContact
from crams.models import ProjectID
from crams.models import ProjectIDSystem
from crams.models import ProjectProvisionDetails
from crams.models import ProjectQuestionResponse
from crams.models import Publication
from crams.models import Request
from crams.models import SupportedInstitution
from crams.api.v1.APIConstants import CLONE
from crams.api.v1.APIConstants import OVERRIDE_READONLY_DATA
from crams.api.v1.APIConstants import DO_NOT_SERIALIZE_REQUESTS_FOR_PROJECT


class ContactSerializer(serializers.ModelSerializer,
                        utilitySerializers.UpdatableSerializer):
    """class ContactSerializer."""

    # check email is unique
    email = serializers.CharField(
        required=True, validators=[
            UniqueValidator(
                queryset=Contact.objects.all())])

    class Meta(object):
        """meta Class."""

        model = Contact
        field = ('id', 'title', 'given_name', 'surname',
                 'email', 'phone', 'organisation')

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return:
        """
        return Contact.objects.create(**validated_data)


def get_contact_lookup_data(search_key):
    """get contact lookup data.

    :param search_key:
    :return:
    """
    return LookupDataModel(Contact).serialize(search_key, ContactSerializer)


class ContactRestrictedFieldSerializer(utilitySerializers.
                                       DynamicFieldsModelSerializer,
                                       serializers.ModelSerializer):
    """class ContactRestrictedFieldSerializer."""

    class Meta(object):
        """meta Class."""

        model = Contact
        fields = ('id', 'title', 'given_name', 'surname', 'email')

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return:
        """
        return Contact.objects.create(**validated_data)


class GrantSerializer(serializers.ModelSerializer):
    """class GrantSerializer."""

    grant_type = utilitySerializers.PrimaryKeyLookupField(
        queryset=GrantType.objects.all(), many=False, required=True, fields=[
            'id', 'description'])  # Grant._meta.get_all_field_names())

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return: :raise ParseError:
        """
        grant_type = validated_data.pop('grant_type', None)

        if grant_type and 'id' in grant_type:
            grant_type = grant_type['id']
            try:
                validated_data['grant_type'] = GrantType.objects.get(
                    id=grant_type)
                return Grant.objects.create(**validated_data)
            except GrantType.DoesNotExist:
                raise ParseError(
                    'Grant Type not found for id {}'.format(grant_type))
            except GrantType.MultipleObjectsReturned:
                raise ParseError(
                    'Multiple Grant Types returned for id {}'
                    .format(grant_type))

        raise ParseError('Grant Type is required')

    class Meta(object):
        """meta Class."""

        model = Grant
        fields = ('id', 'grant_type', 'funding_body_and_scheme',
                  'duration', 'grant_id', 'start_year', 'total_funding')


class PublicationSerializer(serializers.ModelSerializer):
    """class PublicationSerializer."""

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return:
        """
        return Publication.objects.create(**validated_data)

    class Meta(object):
        """meta Class."""

        model = Publication
        fields = ('id', 'reference')


class SupportedInstitutionSerializer(serializers.ModelSerializer):
    """class SupportedInstitutionSerializer."""

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return:
        """
        return SupportedInstitution.objects.create(**validated_data)

    class Meta(object):
        """meta class."""

        model = SupportedInstitution
        fields = ('id', 'institution')


class ProjectQuestionResponseSerializer(utilitySerializers.
                                        AbstractQuestionResponseSerializer):
    """class ProjectQuestionResponseSerializer."""

    class Meta(object):
        """meta class."""

        model = ProjectQuestionResponse
        fields = ('id', 'question_response', 'question')


class DomainSerializer(serializers.ModelSerializer):
    """class DomainSerializer."""

    for_code = utilitySerializers.PrimaryKeyLookupField(
        many=False, queryset=FORCode.objects.all(), fields=[
            'id', 'code', 'description'])

    class Meta(object):
        """meta class."""

        model = Domain
        fields = ('id', 'percentage', 'for_code')

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return: :raise ParseError:
        """
        for_code = validated_data.pop('for_code', None)
        if for_code and 'id' in for_code:
            for_code = for_code['id']
            try:
                validated_data['for_code'] = FORCode.objects.get(id=for_code)
                return Domain.objects.create(**validated_data)
            except FORCode.DoesNotExist:
                raise ParseError(
                    'For code not found for id {}'.format(for_code))
            except FORCode.MultipleObjectsReturned:
                raise ParseError(
                    'Multiple For codes returned for id {}'.format(for_code))

        raise ParseError('For code is required')


class ProjectIDSerializer(serializers.ModelSerializer):
    """class ProjectIDSerializer."""

    system = utilitySerializers.PrimaryKeyLookupField(
        many=False,
        required=True,
        queryset=ProjectIDSystem.objects.all(),
        fields=[
            'id',
            'system'])

    class Meta(object):
        """meta Class."""

        model = ProjectID
        fields = ('id', 'identifier', 'system')

    # noinspection PyUnusedLocal
    def _init_empty(self, str, num):
        ret_dict = dict()
        ret_dict['identifier'] = 'System Identifier for this Project'
        ret_dict['system'] = self.__getitem__(
            'system').to_representation({'id': 1})
        return ret_dict

    def _init_from_project_id_data(self, project_id_data):
        ret_dict = dict()
        ret_dict['identifier'] = project_id_data.get('identifier', None)
        system_data = project_id_data.get('system', None)
        if system_data:
            ret_dict['system'] = self.__getitem__('system').to_representation({
                'id': system_data.get('id', None)})
        return ret_dict

    def validate(self, data):
        return projectid_validators.extract_project_id_save_args(data)

    def create(self, validated_data):
        """

        :param validated_data:
        :return:
        """
        ret = ProjectID.objects.create(
            identifier=validated_data.get('identifier'),
            system=validated_data.get('system_obj'),
            project=validated_data.get('project')
        )
        return ret


class ProjectContactSerializer(serializers.ModelSerializer):
    """class ProjectContactSerializer."""

    contact = utilitySerializers.PrimaryKeyLookupField(
        many=False,
        required=True,
        queryset=Contact.objects.all(),
        fields=[
            'id',
            'email'])
    contact_role = utilitySerializers.PrimaryKeyLookupField(
        many=False,
        required=True,
        queryset=ContactRole.objects.all(),
        fields=[
            'id',
            'name'])

    class Meta(object):
        """meta Class."""

        model = ProjectContact
        fields = ('id', 'contact', 'contact_role')

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return: :raise ParseError:
        """
        contact_id = validated_data.pop('contact', None)
        if contact_id and 'id' in contact_id:
            contact_id = contact_id['id']
            try:
                validated_data['contact'] = Contact.objects.get(id=contact_id)
            except Contact.DoesNotExist:
                raise ParseError(
                    'Contact not found for id {}'.format(contact_id))

        else:
            raise ParseError('Contact Id is required')

        contact_role_id = validated_data.pop('contact_role', None)
        if contact_role_id and 'id' in contact_role_id:
            contact_role_id = contact_role_id['id']
            try:
                validated_data['contact_role'] = ContactRole.objects.get(
                    id=contact_role_id)
                return ProjectContact.objects.create(**validated_data)
            except ProjectContact.DoesNotExist:
                raise ParseError(
                    'ContactRole id does not exist {}'.format(contact_role_id))
            except ProjectContact.MultipleObjectsReturned:
                raise ParseError(
                    'Multiple ContactRole id exists {}'
                    .format(contact_role_id))

        raise ParseError('Contact Role is required')


class ProjectSerializer(utilitySerializers.ActionStateModelSerializer):
    """class ProjectSerializer."""

    # project question response
    project_question_responses = ProjectQuestionResponseSerializer(
        many=True, read_only=False, allow_null=True, required=False)

    # Supported institutions
    institutions = SupportedInstitutionSerializer(many=True, read_only=False)

    # Publication
    publications = PublicationSerializer(
        many=True, read_only=False, allow_null=True, required=False)

    # Grant information
    grants = GrantSerializer(
        many=True, read_only=False, allow_null=True, required=False)

    # ProjectID
    project_ids = ProjectIDSerializer(
        many=True, read_only=False, allow_null=True, required=False)

    # Contacts
    project_contacts = ProjectContactSerializer(
        many=True, read_only=False, allow_null=True, required=False)

    # Project Provision Details
    provision_details = serializers.SerializerMethodField(
        method_name='filter_provision_project')

    # Domains
    domains = DomainSerializer(many=True, read_only=False)

    # Request
    requests = serializers.SerializerMethodField(method_name='filter_requests')

    historic = serializers.SerializerMethodField(method_name='is_historic')

    class Meta(object):
        """class Meta."""

        model = Project
        fields = (
            'id',
            'title',
            'description',
            'historic',
            'notes',
            'project_question_responses',
            'institutions',
            'publications',
            'grants',
            'project_ids',
            'project_contacts',
            'provision_details',
            'domains',
            'requests')
        read_only_fields = ('provision_details',
                            'creation_ts',
                            'last_modified_ts')

    @staticmethod
    def is_historic(project_obj):
        return project_obj.parent_project is not None

    def filter_provision_project(self, project_obj):
        """

        :param project_obj:
        :return:
        """
        if hasattr(self, 'cramsActionState'):
            user_obj = self.cramsActionState.rest_request.user
            context = utilitySerializers.\
                ProvisionDetailsSerializer.build_context_obj(user_obj)
        else:
            context = utilitySerializers. \
                ProvisionDetailsSerializer.hide_error_msg_context()

        ret_list = []
        for p in project_obj.linked_provisiondetails.all():
            pd_serializer = utilitySerializers.\
                ProvisionDetailsSerializer(p.provision_details,
                                           context=context)
            ret_list.append(pd_serializer.data)

        return ret_list

    def filter_requests(self, project_obj):
        """filter requests.

        :param project_obj:
        :return:
        """
        # Filter project requests based on Url parameters
        # To get URL params use self.context['request'].query_params(xxx,None)
        context_request = self.context['request']
        request_id = context_request.query_params.get('request_id', None)
        if request_id:
            # , parent_request__isnull=True)
            requests = project_obj.requests.filter(id=request_id)
        else:
            requests = project_obj.requests.filter(parent_request__isnull=True)

        ret_list = []
        override_data = self.context.get(OVERRIDE_READONLY_DATA, None)
        serialize_requests = not (override_data and
                                  DO_NOT_SERIALIZE_REQUESTS_FOR_PROJECT in
                                  override_data)

        if serialize_requests:
            req_context = {'request': context_request}
            for req in requests:
                req_serializer = requestSerializers.\
                    CramsRequestSerializer(req, context=req_context)
                ret_list.append(req_serializer.data)

        return ret_list

    def _add_applicant_contact(self, new_project):
        if not self.context:
            raise ParseError(
                'ProjectSerializer: "self.context" object not found, ' +
                'required to identify current user.')

        try:
            applicant_role = ContactRole.objects.get(name=APPLICANT)
        except ContactRole.DoesNotExist:
            raise ParseError('Data Error: Contact Role Applicant not found')

        current_user = self.context['request'].user
        contact = Contact.objects.filter(email=current_user.email).first()
        if not contact:
            contact = Contact.objects.create(
                given_name=current_user.first_name,
                surname=current_user.last_name,
                email=current_user.email)

        return ProjectContact.objects.create(
            project=new_project,
            contact=contact,
            contact_role=applicant_role)

    def validate(self, data):
        """validate.

        :param data:
        :return: :raise ValidationError:
        """
        self._setActionState()
        if self.cramsActionState.error_message:
            raise ValidationError(
                'CramsRequestSerializer: ' +
                self.cramsActionState.error_message)

        if self.cramsActionState.is_update_action:
            if 'project_contacts' not in data or len(
                    data['project_contacts']) < 1:
                raise ValidationError(
                    'project_contacts: ' + 'A project contact is required')

            project = self.cramsActionState.existing_instance
            if project.parent_project:
                concurrent_user = project.parent_project.updated_by
                raise ParseError('concurrent update: {} has updated '
                                 'project, please refresh and try again'
                                 .format(repr(concurrent_user)))

            request_ids = project.requests.values_list('id', flat=True)

            msg_suffix = 'cannot be changed after approval for Nectar Project'
            if Request.objects.filter(
                    request_status__code=REQUEST_STATUS_APPROVED,
                    parent_request__in=request_ids).exists():

                nectar_system = get_system_obj({'system': SYSTEM_NECTAR})
                nectar_project_id = project.project_ids.filter(
                    system=nectar_system)
                if nectar_project_id.exists():
                    if project.description != data['description']:
                        raise ValidationError(
                            'project_decription: ' + msg_suffix)

                    existing_pid = nectar_project_id.first()
                    for p_id in data.get('project_ids'):
                        p_id_system = get_system_obj(p_id.get('system'))
                        if p_id_system == nectar_system:
                            if existing_pid.identifier != p_id['identifier']:
                                raise ValidationError(
                                    'project_id_identifier: ' + msg_suffix)

        # Validate project ids after concurrent update validation
        project_ids = data.get('project_ids')
        if project_ids:
            existing_instance = self.cramsActionState.existing_instance
            self.setup_project_ids(project_ids, existing_instance)

        return data

    @classmethod
    def setup_project_ids(cls, project_ids, project):
        for p_id_data in project_ids:
            proj_id_serializer = ProjectIDSerializer(
                data=p_id_data,
                validators=[
                    projectid_validators.ValidateProjectIDPrefix(),
                    projectid_validators.UniqueSystemProjectIDValidator(
                        project)]
            )
            proj_id_serializer.is_valid(raise_exception=True)
            p_id_data['serializer'] = proj_id_serializer

    @transaction.atomic
    def update(self, instance, validated_data):
        # for partial updates with no data other than override data,
        # the validate method would not have been invoked, hence repeat
        # actionState setup
        """update.

        :param instance:
        :param validated_data:
        :return:
        """
        self._setActionState()

        new_project = self.save_project(validated_data, instance)
        old_project_instance = instance
        old_project_instance.parent_project = new_project
        old_project_instance.save()
        Project.objects.filter(parent_project=old_project_instance).update(
            parent_project=new_project)
        return new_project

    @transaction.atomic
    def create(self, validated_data):
        """create.

        :param validated_data:
        :return:
        """
        new_project = self.save_project(validated_data, None)
        self._add_applicant_contact(new_project)
        return new_project

    def save_project(self, validated_data, existing_project_instance):
        """save project.

        :param validated_data:
        :param existing_project_instance:
        :return: :raise ParseError:
        """

        parent_project = validated_data.pop('parent_project', None)
        if parent_project:
            raise ParseError(
                'Projects with parent_project value set are historic, ' +
                'readonly records. Update fail')

        # Project Question responses
        proj_question_responses_data = validated_data.pop(
            'project_question_responses', None)

        # Supported institutions
        institutions_data = validated_data.pop('institutions', None)

        # Publications
        publications_data = validated_data.pop('publications', None)

        # Grants
        grants_data = validated_data.pop('grants', None)

        # Project identifiers
        proj_identifiers_data = validated_data.pop('project_ids', None)

        # Project contacts
        proj_contacts_data = validated_data.pop('project_contacts', None)

        # Domains
        domains_data = validated_data.pop('domains', None)

        # Requests
        # Do not comment, we need to pop this out and use request data from
        # self.initial_data
        validated_data.pop('requests', None)

        # Project
        current_user = self.context['request'].user
        validated_data['updated_by'] = current_user
        existing_request_instances = {}
        provision_details_exists = False
        if existing_project_instance:
            provision_details_exists = existing_project_instance.\
                linked_provisiondetails.exists()
            validated_data['created_by'] = existing_project_instance.created_by
            for existing_request_instance in \
                    existing_project_instance.requests.all():
                existing_request_instances[
                    existing_request_instance.id] = existing_request_instance
        else:
            validated_data['created_by'] = current_user

        project = Project.objects.create(**validated_data)
        pd_context = utilitySerializers.\
            ProvisionDetailsSerializer.show_error_msg_context()
        if provision_details_exists:
            # note: Provision details are updated at provision time
            # so we are re-using provision_details, instead of a deep copy
            for ppd in existing_project_instance.\
                    linked_provisiondetails.all():
                temp = utilitySerializers.\
                    ProvisionDetailsSerializer(ppd.provision_details,
                                               context=pd_context)
                pd_s = utilitySerializers.\
                    ProvisionDetailsSerializer(data=temp.data)
                pd_s.is_valid(True)
                ProjectProvisionDetails.objects.create(
                    project=project,
                    provision_details=pd_s.save())

        if proj_question_responses_data:
            for proj_question_response_data in proj_question_responses_data:
                proj_question_resp_serializer = \
                    ProjectQuestionResponseSerializer(
                        data=proj_question_response_data)
                proj_question_resp_serializer.is_valid(raise_exception=True)
                proj_question_resp_serializer.save(project=project)

        if institutions_data:
            for supported_inst in institutions_data:
                supported_inst_serializer = SupportedInstitutionSerializer(
                    data=supported_inst)
                supported_inst_serializer.is_valid(raise_exception=True)
                supported_inst_serializer.save(project=project)

        if publications_data:
            for pub_data in publications_data:
                pub_serializer = PublicationSerializer(data=pub_data)
                pub_serializer.is_valid(raise_exception=True)
                pub_serializer.save(project=project)

        if grants_data:
            for grant_data in grants_data:
                grant_serializer = GrantSerializer(data=grant_data)
                grant_serializer.is_valid(raise_exception=True)
                grant_serializer.save(project=project)

        if proj_identifiers_data:
            for p_id_data in proj_identifiers_data:
                proj_id_serializer = p_id_data.get('serializer')
                if proj_id_serializer:
                    proj_id_serializer.save(project=project)

        if proj_contacts_data:
            for proj_contact_data in proj_contacts_data:
                project_contacts_serializer = ProjectContactSerializer(
                    data=proj_contact_data)
                project_contacts_serializer.is_valid(raise_exception=True)
                project_contacts_serializer.save(project=project)

        if domains_data:
            for domain_data in domains_data:
                domain_serializer = DomainSerializer(data=domain_data)
                domain_serializer.is_valid(raise_exception=True)
                domain_serializer.save(project=project)

        # Do not use the parsed validatedData, it does not contain request_id
        requests = self.initial_data.pop('requests', None)
        if requests:
            context = {}
            context['request'] = self.context['request']
            for requestData in requests:
                parent_request = requestData.pop('parent_request', None)
                if parent_request:
                    # These are historic requests, should not be updated.
                    continue

                # will be set later with new project
                requestData.pop('project', None)
                request_id = requestData.pop('id', None)
                if request_id:
                    existing_request_instance = existing_request_instances.pop(
                        request_id, None)
                    if existing_request_instance:
                        request_serializer = \
                            requestSerializers.CramsRequestSerializer(
                                existing_request_instance,
                                data=requestData,
                                context=context)
                    else:
                        raise ParseError(
                            'Project/Request mismatch, cannot find request' +
                            ' with id {}'.format(repr(request_id)))
                else:
                    request_serializer = \
                        requestSerializers.CramsRequestSerializer(
                            data=requestData, context=context)

                request_serializer.is_valid(raise_exception=True)

                request_serializer.save(project=project)

            # copy remaining requests across
            # request_status is read_only, hence cannot be passed in updateData
            context[OVERRIDE_READONLY_DATA] = {CLONE: True}
            for idKey in existing_request_instances:
                remaining_instance = existing_request_instances[idKey]
                if not remaining_instance.parent_request:
                    request_serializer = \
                        requestSerializers.CramsRequestSerializer(
                            remaining_instance, data={},
                            partial=True, context=context)
                    request_serializer.is_valid(raise_exception=True)
                    request_serializer.save(project=project)

        return project


class ReadOnlyProjectSerializer(ProjectSerializer):
    """class ReadOnlyProjectSerializer."""

    def create(self, validated_data):
        """create.

        :param validated_data:
        :raise ParseError:
        """
        raise ParseError('Create not allowed ')

    def update(self, instance, validated_data):
        """update.

        :param instance:
        :param validated_data:
        :raise ParseError:
        """
        raise ParseError('Update not allowed ')
