# coding=utf-8
"""RequestSerializers."""

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
import logging
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import PrimaryKeyRelatedField

from crams import django_utils
from crams import settings
from crams.DBConstants import ADMIN_STATES
from crams.DBConstants import APPROVAL_STATES
from crams.DBConstants import DECLINED_STATES
from crams.DBConstants import NEW_REQUEST_STATUS
from crams.roleUtils import FUNDING_BODY_NECTAR
from crams.roleUtils import FB_REPLY_TO_MAP
from crams.lang_utils import strip_lower
from crams.DBConstants import LEGACY_STATES
from crams.DBConstants import NON_ADMIN_STATES
from crams.DBConstants import REQUEST_STATUS_DECLINED
from crams.DBConstants import REQUEST_STATUS_NEW
from crams.DBConstants import REQUEST_STATUS_PROVISIONED
from crams.DBConstants import REQUEST_STATUS_SUBMITTED
from crams.DBConstants import REQUEST_STATUS_UPDATE_OR_EXTEND
from crams.DBConstants import REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED
from crams.mail import mail_sender
from crams.models import ComputeProduct
from crams.models import ComputeRequest
from crams.models import ComputeRequestQuestionResponse
from crams.models import FundingScheme
from crams.models import Project
from crams.models import Request
from crams.models import AllocationHome
from crams.models import RequestQuestionResponse
from crams.models import RequestStatus
from crams.models import StorageRequest
from crams.models import StorageRequestQuestionResponse
from crams.models import NotificationTemplate
from crams.api.v1.dataUtils import lookupData
from crams.api.v1.serializers.lookupSerializers import \
    StorageProductZoneOnlySerializer
from crams.api.v1.serializers.utilitySerializers import \
    AbstractQuestionResponseSerializer, ProvisionDetailsSerializer
from crams.api.v1.serializers.utilitySerializers import \
     ActionStateModelSerializer
from crams.api.v1.serializers import projectSerializers
from crams.api.v1.serializers import utilitySerializers
from crams.api.v1.APIConstants import DO_NOT_SERIALIZE_REQUESTS_FOR_PROJECT

User = get_user_model()
LOG = logging.getLogger(__name__)


class AllocationHomeSerializer(utilitySerializers.ReadOnlyModelSerializer):
    """class AllocationHomeSerializer."""

    class Meta(object):
        model = AllocationHome
        fields = ('id', 'code')


class ComputeQuestionResponseSerializer(AbstractQuestionResponseSerializer):
    """class ComputeQuestionResponseSerializer."""

    class Meta(object):
        model = ComputeRequestQuestionResponse
        fields = ('id', 'question_response', 'question')


class ProductRequestSerializer(ModelSerializer):
    PR_CONTEXT = 'pr_context'
    provision_details = serializers.SerializerMethodField(
        method_name='sanitize_provision_details')

    @classmethod
    def show_error_msg_context(cls):
        return {
            cls.PR_CONTEXT: ProvisionDetailsSerializer.show_error_msg_context()
        }

    @classmethod
    def hide_error_msg_context(cls):
        return {
            cls.PR_CONTEXT: ProvisionDetailsSerializer.hide_error_msg_context()
        }

    @classmethod
    def build_context_obj(cls, user_obj, funding_body_obj):
        return {
            cls.PR_CONTEXT: ProvisionDetailsSerializer.build_context_obj(
                user_obj, funding_body_obj)
        }

    def sanitize_provision_details(self, product_request_obj):
        default_pd = ProvisionDetailsSerializer.hide_error_msg_context()
        if self.context:
            pd_context = self.context.get(self.PR_CONTEXT, default_pd)
        else:
            pd_context = default_pd

        pd_serializer = ProvisionDetailsSerializer(
            product_request_obj.provision_details,
            context=pd_context)

        return pd_serializer.data


class ComputeRequestSerializer(ProductRequestSerializer):
    """class ComputeRequestSerializer."""

    compute_product = utilitySerializers.PrimaryKeyLookupField(
        many=False, required=True, fields=[
            'id', 'name'], queryset=ComputeProduct.objects.all())
    compute_question_responses = ComputeQuestionResponseSerializer(
        many=True, read_only=False, allow_null=True, required=False)

    class Meta(object):
        model = ComputeRequest
        fields = (
            'id',
            'instances',
            'approved_instances',
            'cores',
            'approved_cores',
            'core_hours',
            'approved_core_hours',
            'compute_product',
            'compute_question_responses',
            'provision_details')
        read_only_fields = ('provision_details')

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return compute_request:
        """
        compute_product = validated_data.pop('compute_product', None)
        if not compute_product or 'id' not in compute_product:
            raise ParseError('Compute product is required')

        compute_product_id = compute_product['id']
        compute_question_responses = validated_data.pop(
            'compute_question_responses', None)

        provision_details = validated_data.pop('provision_details', None)
        if provision_details:
            pSerializer = ProvisionDetailsSerializer(
                data=provision_details, context=self.context)
            pSerializer.is_valid(raise_exception=True)
            validated_data['provision_details'] = pSerializer.save()

        validated_data['compute_product'] = \
            lookupData.get_compute_product_obj({'pk': compute_product_id})

        compute_request = ComputeRequest.objects.create(**validated_data)
        if compute_question_responses:
            for cqr in compute_question_responses:
                cqrSerializer = ComputeQuestionResponseSerializer(data=cqr)
                cqrSerializer.is_valid(raise_exception=True)
                cqrSerializer.save(compute_request=compute_request)

        return compute_request


class StorageQuestionResponseSerializer(AbstractQuestionResponseSerializer):
    """class StorageQuestionResponseSerializer."""

    class Meta(object):
        model = StorageRequestQuestionResponse
        fields = ('id', 'question_response', 'question')


class StorageRequestSerializer(ProductRequestSerializer):
    """class StorageRequestSerializer."""

    storage_product = StorageProductZoneOnlySerializer(required=True)
    storage_question_responses = StorageQuestionResponseSerializer(
        many=True, read_only=False, allow_null=True, required=False)

    class Meta(object):
        model = StorageRequest
        fields = ('id', 'quota', 'approved_quota', 'storage_product',
                  'storage_question_responses', 'provision_details')
        read_only_fields = ('provision_details')

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return storage_request:
        """
        # not used, use initial_data instead
        validated_data.pop('storage_product', None)
        storage_product = self.initial_data.pop('storage_product', None)
        if not storage_product or 'id' not in storage_product:
            raise ParseError('Storage product is required')

        storage_product_id = storage_product['id']
        storage_question_responses = validated_data.pop(
            'storage_question_responses', None)

        provision_details = validated_data.pop('provision_details', None)
        if provision_details:
            pSerializer = ProvisionDetailsSerializer(
                data=provision_details, context=self.context)
            pSerializer.is_valid(raise_exception=True)
            validated_data['provision_details'] = pSerializer.save()

        validated_data['storage_product'] = \
            lookupData.get_storage_product_obj({'pk': storage_product_id})

        storage_request = StorageRequest.objects.create(**validated_data)

        if storage_question_responses:
            for sqr in storage_question_responses:
                sqrSerializer = StorageQuestionResponseSerializer(data=sqr)
                sqrSerializer.is_valid(raise_exception=True)
                sqrSerializer.save(storage_request=storage_request)

        return storage_request


class RequestQuestionResponseSerializer(AbstractQuestionResponseSerializer):
    """class RequestQuestionResponseSerializer."""

    class Meta(object):
        model = RequestQuestionResponse
        fields = ('id', 'question_response', 'question')


class RequestHistorySerializer(ModelSerializer):
    """class RequestHistorySerializer."""

    project = utilitySerializers.PrimaryKeyLookupField(
        many=False, fields=['id', 'title'], read_only=True, model=Project)
    request_status = utilitySerializers.PrimaryKeyLookupField(
        many=False,
        fields=[
            'code',
            'status'],
        read_only=True,
        model=RequestStatus)

    class Meta(object):
        model = Request
        fields = ('id', 'request_status', 'project',
                  'last_modified_ts', 'parent_request')
        read_only_fields = ('request_status', 'project',
                            'last_modified_ts', 'parent_request')


class CramsRequestSerializer(ActionStateModelSerializer):
    """class CramsRequestSerializer."""

    # Make sure all foreign keys that are not updated from input are set to
    # PrimaryKeyRelatedField or its derivate PrimaryKeyLookupField
    project = PrimaryKeyRelatedField(
        many=False,
        required=False,
        queryset=Project.objects.filter(
            parent_project__isnull=True))

    compute_requests = serializers.SerializerMethodField(
        method_name='populate_compute_request')

    storage_requests = serializers.SerializerMethodField(
        method_name='populate_storage_request')

    # request question response
    request_question_responses = RequestQuestionResponseSerializer(
        many=True, read_only=False)

    request_status = utilitySerializers.PrimaryKeyLookupField(
        many=False, read_only=True, fields=[
            'id', 'code', 'status'], model=RequestStatus)

    funding_scheme = utilitySerializers.PrimaryKeyLookupField(
        many=False, required=True, fields=[
            'id', 'funding_scheme'], queryset=FundingScheme.objects.all())

    allocation_home = serializers.SlugRelatedField(
        many=False, slug_field='code', required=False, allow_null=True,
        queryset=AllocationHome.objects.all())

    created_by = utilitySerializers.PrimaryKeyLookupField(
        many=False,
        required=True,
        fields=[
            'id',
            'email',
            'first_name',
            'last_name'],
        queryset=User.objects.all())

    updated_by = utilitySerializers.PrimaryKeyLookupField(
        many=False,
        required=True,
        fields=[
            'id',
            'email',
            'first_name',
            'last_name'],
        queryset=User.objects.all())

    historic = serializers.SerializerMethodField(method_name='is_historic')

    class Meta(object):
        model = Request
        field = ('id', 'start_date', 'end_date', 'approval_notes', 'historic',
                 'compute_requests', 'storage_requests', 'funding_scheme',
                 'national_percent', 'allocation_home')
        read_only_fields = (
            'creation_ts', 'last_modified_ts', 'request_status')

    @staticmethod
    def is_historic(request_obj):
        return request_obj.parent_request is not None

    def populate_compute_request(self, request_obj):
        user = None
        if hasattr(self, 'cramsActionState'):
            user = self.cramsActionState.rest_request.user
        pd_context = ComputeRequestSerializer.build_context_obj(
            user, request_obj.funding_scheme.funding_body)

        ret_list = []
        for c_req in request_obj.compute_requests.all():
            serializer = ComputeRequestSerializer(c_req, context=pd_context)
            ret_list.append(serializer.data)
        return ret_list

    def populate_storage_request(self, request_obj):
        user = None
        if hasattr(self, 'cramsActionState'):
            user = self.cramsActionState.rest_request.user
        pd_context = StorageRequestSerializer.build_context_obj(
            user, request_obj.funding_scheme.funding_body)

        ret_list = []
        for s_req in request_obj.storage_requests.all():
            serializer = StorageRequestSerializer(s_req, context=pd_context)
            ret_list.append(serializer.data)
        return ret_list

    @classmethod
    def validate_allocation_percentage(
            cls, crams_action_state, national_percent, allocation_home_obj):
        if crams_action_state.is_create_action:
            if national_percent or allocation_home_obj:
                raise ValidationError(
                    'allocation percent/node can only be set at approval time')
            return 100

        request_obj = crams_action_state.existing_instance
        if national_percent is None:
            if request_obj.request_status not in NEW_REQUEST_STATUS:
                raise ValidationError(
                    'request allocation percent is required')
        if national_percent == 100 and allocation_home_obj:
            raise ValidationError(
                'Allocation Node cannot be set if National Percent is 100')
        elif national_percent < 100 and not allocation_home_obj:
            raise ValidationError(
                'Allocation Node must be set if National Percent is not 100')

        if not crams_action_state.is_partial_action:
            if allocation_home_obj != request_obj.allocation_home or \
               national_percent != request_obj.national_percent:
                raise ValidationError(
                    'allocation percent/node can only be set at approval time')

        return national_percent

    def validate(self, data):
        """validate.

        :param data:
        :return validated_data:
        """
        self._setActionState()
        cramsActionState = self.cramsActionState
        if cramsActionState.error_message:
            raise ValidationError(
                'CramsRequestSerializer: ' +
                self.cramsActionState.error_message)

        instance = cramsActionState.existing_instance

        # validate and setup Node information for Allocation
        allocation_home_obj = data.get('allocation_home')
        if not allocation_home_obj and instance:
            allocation_home_obj = instance.allocation_home
        if allocation_home_obj:
            data['allocation_home'] = allocation_home_obj

        in_national_percent = data.get('national_percent')
        if not in_national_percent and instance:
            in_national_percent = instance.national_percent
        data['national_percent'] = self.validate_allocation_percentage(
            cramsActionState, in_national_percent, allocation_home_obj)

        if cramsActionState.is_create_action:
            if 'funding_scheme' not in data:
                raise ValidationError({
                    'funding_scheme': 'This field is required.'
                })

            if 'start_date' not in data:
                raise ValidationError({
                    'start_date': 'This field is required.'
                })

            if 'end_date' not in data:
                raise ValidationError({
                    'end_date': 'This field is required.'
                })

        if cramsActionState.is_partial_action:
            if (cramsActionState.override_data and 'request_status' in
                    cramsActionState.override_data):
                inStatusCode = cramsActionState.override_data['request_status']
                existingStatusCode = (instance.request_status.code)

                if (inStatusCode in LEGACY_STATES or existingStatusCode
                        in LEGACY_STATES):
                    raise ValidationError('Request Status : legacy states \
                                          partial update not implemented yet \
                                          {}/{}'.format(inStatusCode,
                                                        existingStatusCode))

                if inStatusCode not in ADMIN_STATES:
                    raise ValidationError('Request Status {}: partial update \
                                          denied, Not an Admin action'
                                          .format(inStatusCode))

                if existingStatusCode == inStatusCode:
                    raise ValidationError(
                        'Request Status: Action cancelled current state is '
                        'same as new state {}'.format(
                            instance.request_status.status))

                elif existingStatusCode in DECLINED_STATES:
                    if inStatusCode not in [
                            REQUEST_STATUS_UPDATE_OR_EXTEND,
                            REQUEST_STATUS_SUBMITTED]:
                        raise ValidationError('Request Status: Declined \
                                               applications can only move \
                                               to edit states')
                    elif (existingStatusCode ==
                            REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED and
                            inStatusCode != REQUEST_STATUS_UPDATE_OR_EXTEND):
                        raise ValidationError('Request Status: requests in \
                                              extend_decline_status can only \
                                              move to update_or_extend status')

                    elif (existingStatusCode == REQUEST_STATUS_DECLINED and
                            inStatusCode != REQUEST_STATUS_SUBMITTED):
                        raise ValidationError('Request Status: requests in \
                                              declined status can only move \
                                              to submitted status')

        elif cramsActionState.is_update_action:
            inStatusCodeDict = data.get('request_status', None)
            if inStatusCodeDict:
                raise ValidationError('Request Status: status is a \
                                      calculated value, cannot be set')

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        """update.

        :para instance:
        :param validated_data:
        :return new_request:
        """
        # Cannot update request being provisioned
        if (self.cramsActionState.is_update_action and
                self.instance.request_status.code in APPROVAL_STATES):
            if not (self.cramsActionState.is_partial_action and
                    self.cramsActionState.override_data):
                raise ValidationError({'request id {}'
                                       .format(self.instance.id):
                                       'Request cannot updated while \
                                       being provisioned'})

        newRequest = self._saveRequest(validated_data, instance)
        # update parent_request property for the historic project, required to
        # identify list for history
        instance.parent_request = newRequest
        instance.save()
        Request.objects.filter(parent_request=instance).update(
            parent_request=newRequest)

        return newRequest

    @transaction.atomic
    def create(self, validated_data):
        """create.

        :param validated_data:
        :return new_request:
        """
        return self._saveRequest(validated_data, None)

    def _saveRequest(self, validated_data, existingRequestInstance):

        cramsActionState = self.cramsActionState
        if not cramsActionState:
            raise ParseError('CramsRequestSerializer.saveRequest: ActionState \
                             not found, contact tech support')

        parent_request = validated_data.pop('parent_request', None)
        if parent_request:
            raise ParseError('Requests with parent_request value set \
                             are historic, readonly records. Update fail')

        # Request Question responses
        request_question_responses_data = validated_data.pop(
            'request_question_responses', None)

        # Set funding scheme
        funding_scheme = validated_data.pop('funding_scheme', None)
        if funding_scheme and 'id' in funding_scheme:
            funding_scheme_id = funding_scheme['id']
            try:
                fundingSchemeInstance = FundingScheme.objects.get(
                    pk=funding_scheme_id)
            except FundingScheme.DoesNotExist:
                raise ParseError('Funding Scheme not found for id {}'
                                 .format(funding_scheme_id))
            except FundingScheme.MultipleObjectsReturned:
                raise ParseError('Multiple Funding Schemes found for id {}'
                                 .format(funding_scheme_id))
        elif not cramsActionState.is_create_action:  # partial update or Clone
            fundingSchemeInstance = existingRequestInstance.funding_scheme
        else:
            raise ParseError('Request funding_scheme could not be determined')
        validated_data['funding_scheme'] = fundingSchemeInstance

        # set Request Status
        requestStatusInstance = self.evaluateRequestStatus(
            fundingSchemeInstance, cramsActionState)
        if not requestStatusInstance:
            raise ParseError('Request status could not be determined')
        validated_data['request_status'] = requestStatusInstance

        # set remaining fields
        current_user = cramsActionState.rest_request.user
        validated_data['updated_by'] = current_user
        if cramsActionState.is_create_action:
            validated_data['created_by'] = current_user
            validated_data['approval_notes'] = None
        else:  # partial update  or Clone
            if 'start_date' not in validated_data:
                validated_data[
                    'start_date'] = existingRequestInstance.start_date

            if 'end_date' not in validated_data:
                validated_data['end_date'] = existingRequestInstance.end_date

            if 'project' not in validated_data:
                validated_data['project'] = existingRequestInstance.project

            validated_data['creation_ts'] = existingRequestInstance.creation_ts
            validated_data['created_by'] = existingRequestInstance.created_by
            if cramsActionState.is_clone_action:
                validated_data[
                    'approval_notes'] = existingRequestInstance.approval_notes
                validated_data['last_modified_ts'] = \
                    existingRequestInstance.last_modified_ts
                validated_data[
                    'updated_by'] = existingRequestInstance.updated_by
            elif requestStatusInstance.code in NON_ADMIN_STATES:
                validated_data['approval_notes'] = None

        request = Request.objects.create(**validated_data)

        # using serializers.SerializerMethodField makes field as read-only.
        # fetch compute request_data from initial data
        compute_requests_data = self.initial_data.get('compute_requests', None)
        pd_context = ComputeRequestSerializer.show_error_msg_context()
        if compute_requests_data:
            for compute_req_data in compute_requests_data:
                compute_request = ComputeRequestSerializer(
                    data=compute_req_data, context=self.context)
                compute_request.is_valid(raise_exception=True)
                compute_request.save(request=request)
        elif not cramsActionState.is_create_action:  # partial update  or Clone
            for computeInstance in \
                    existingRequestInstance.compute_requests.all():
                # use the compute serializer instead of creating
                # a new model instance directly.
                #    - This allows for business logic to be
                #       encapsulated in one place, i.e., the serializer.
                temp = ComputeRequestSerializer(computeInstance,
                                                context=pd_context)
                compute_request = ComputeRequestSerializer(
                    data=temp.data, context=self.context)
                # cannot call save without checking is_valid()
                compute_request.is_valid(raise_exception=True)
                compute_request.save(request=request)

        # using serializers.SerializerMethodField makes field as read-only.
        # fetch storage request_data from initial data
        storage_requests_data = self.initial_data.get('storage_requests', None)
        pd_context = StorageRequestSerializer.show_error_msg_context()
        if storage_requests_data:
            for storage_req_data in storage_requests_data:
                storage_request = StorageRequestSerializer(
                    data=storage_req_data, context=self.context)
                storage_request.is_valid(raise_exception=True)
                storage_request.save(request=request)
        elif not cramsActionState.is_create_action:  # partial update or Clone
            for storageInstance in \
                    existingRequestInstance.storage_requests.all():
                temp = StorageRequestSerializer(storageInstance,
                                                context=pd_context)
                storage_request = StorageRequestSerializer(
                    data=temp.data, context=self.context)
                storage_request.is_valid(raise_exception=True)
                storage_request.save(request=request)

        if request_question_responses_data:
            for req_question_response_data in request_question_responses_data:
                req_question_resp_serializer =\
                    RequestQuestionResponseSerializer(
                        data=req_question_response_data)
                req_question_resp_serializer.is_valid(raise_exception=True)
                req_question_resp_serializer.save(request=request)
        elif not cramsActionState.is_create_action:  # partial update or Clone
            for reqQuestionInstance in \
                    existingRequestInstance.request_question_responses.all():
                temp = RequestQuestionResponseSerializer(reqQuestionInstance)
                req_question_resp_serializer =\
                    RequestQuestionResponseSerializer(data=temp.data)
                req_question_resp_serializer.is_valid(raise_exception=True)
                req_question_resp_serializer.save(request=request)
        # send email notification
        if not cramsActionState.is_clone_action:
            self.send_notification(request)

        return request

    @classmethod
    def evaluateRequestStatus(cls, fundingSchemeInstance, cramsActionState):
        """evaluate request status.

        :param cls:
        :param fundingSchemeInstance:
        :param cramsActionState:
        :return:
        """
        if not cramsActionState:
            raise ParseError('CramsActionState required')
        existingRequestInstance = cramsActionState.existing_instance

        if cramsActionState.is_create_action:
            status_code = REQUEST_STATUS_NEW
            if fundingSchemeInstance and \
                    fundingSchemeInstance.funding_body.name.strip() ==\
                    FUNDING_BODY_NECTAR:
                status_code = REQUEST_STATUS_SUBMITTED
            return RequestStatus.objects.get(code=status_code)

        move_to_extend_status_codes = [
            REQUEST_STATUS_UPDATE_OR_EXTEND,
            REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED,
            REQUEST_STATUS_PROVISIONED]
        if cramsActionState.is_clone_action:
            status_code = existingRequestInstance.request_status.code
        elif (cramsActionState.override_data and
                'request_status' in cramsActionState.override_data):
            status_code = cramsActionState.override_data['request_status']
        elif (existingRequestInstance.request_status.code ==
                REQUEST_STATUS_NEW or
                existingRequestInstance.request_status.code ==
                REQUEST_STATUS_DECLINED):
            status_code = REQUEST_STATUS_SUBMITTED
        elif (existingRequestInstance.request_status.code in
                move_to_extend_status_codes):
            status_code = REQUEST_STATUS_UPDATE_OR_EXTEND
        else:
            status_code = existingRequestInstance.request_status.code

        return RequestStatus.objects.get(code=status_code)

    def populate_email_dict_for_request(self, alloc_request):
        serializer = CramsRequestSerializer(alloc_request,
                                            context=self.context)
        ret_dict = serializer.data

        project_context = {'request': self.context['request'],
                           DO_NOT_SERIALIZE_REQUESTS_FOR_PROJECT: True}
        project_serializer = projectSerializers.ProjectSerializer(
            alloc_request.project, many=False, context=project_context)
        ret_dict['project'] = project_serializer.data
        fb_name = alloc_request.funding_scheme.funding_body.name
        base_url = django_utils.get_funding_body_request_url(fb_name)
        ret_dict['client_request_url'] = base_url + str(alloc_request.id)

        return ret_dict

    def send_notification(self, alloc_req):
        """send notification.

        :param alloc_req:
        """
        try:
            template_obj = NotificationTemplate.objects.get(
                request_status=alloc_req.request_status,
                funding_body=alloc_req.funding_scheme.funding_body
            )
        except NotificationTemplate.DoesNotExist:
            return

        template = template_obj.template_file_path

        mail_content = self.populate_email_dict_for_request(alloc_req)
        try:
            desc = alloc_req.project.description
            subject = 'Allocation request - ' + desc

            sender = settings.EMAIL_SENDER
            recipient_list = get_request_contact_email_ids(alloc_req)
            funding_body = alloc_req.funding_scheme.funding_body
            cc_list = None
            if template_obj.alert_funding_body:
                if funding_body.email:
                    cc_list = [funding_body.email]
                else:
                    p_msg = 'Email not found, Unable to send notification to '
                    LOG.error(p_msg + funding_body.name)
            reply_to = FB_REPLY_TO_MAP.get(strip_lower(funding_body.name))
            mail_sender.send_notification(
                sender=sender,
                subject=subject,
                mail_content=mail_content,
                template_name=template,
                recipient_list=recipient_list,
                cc_list=cc_list,
                bcc_list=None,
                reply_to=reply_to)
        except Exception as e:
            error_message = '{} : Project - {}'.format(repr(e), desc)
            LOG.error(error_message)
            if settings.DEBUG:
                raise Exception(error_message)


class ReadOnlyCramsRequestSerializer(CramsRequestSerializer):
    """class ReadOnlyCramsRequestSerializer."""

    def create(self, validated_data):
        """create.

        :param validated_data:
        """
        raise ParseError('Create not allowed ')

    def update(self, instance, validated_data):
        """update.

        :param instance:
        :param validated_data:
        """
        raise ParseError('Update not allowed ')


def get_request_contact_email_ids(allocation_request):
    ret_set = set()
    for project_contact in allocation_request.project.project_contacts.all():
        ret_set.add(project_contact.contact.email)

    # Fix for missing applicant notification. Applicants are not added
    # to contacts until after Notifications are sent at create time.
    if allocation_request.updated_by.email not in ret_set:
        ret_set.add(allocation_request.updated_by.email)

    return list(ret_set)
