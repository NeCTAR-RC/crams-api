# coding=utf-8
"""Provision Serializers."""
from django.db.models import Q
from django.db import transaction
import pprint
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.serializers import SlugRelatedField

from crams.DBConstants import REQUEST_STATUS_APPROVED
from crams.DBConstants import REQUEST_STATUS_LEGACY_APPROVED
from crams.DBConstants import REQUEST_STATUS_PROVISIONED
from crams.dbUtils import fetch_active_provider_object_for_user
from crams.models import ComputeProduct
from crams.models import ComputeRequest
from crams.models import Project
from crams.models import ProjectProvisionDetails
from crams.models import Provider
from crams.models import ProvisionDetails
from crams.models import Request
from crams.models import StorageProduct
from crams.models import StorageRequest

from crams_api.APIConstants import OVERRIDE_READONLY_DATA
from crams_api.APIConstants import DO_NOT_OVERRIDE_PROVISION_DETAILS


from crams_api.dataUtils.lookupData import get_compute_product_obj
from crams_api.dataUtils.lookupData import get_storage_product_obj
from crams_api.serializers.projectSerializers import ProjectIDSerializer
from crams_api.serializers.projectSerializers import ReadOnlyProjectSerializer
from crams_api.serializers.requestSerializers import CramsRequestSerializer
from crams_api.serializers.requestSerializers import \
    ReadOnlyCramsRequestSerializer
from crams_api.serializers.utilitySerializers import PrimaryKeyLookupField
from crams_api.serializers.utilitySerializers import ProvisionDetailsSerializer
__author__ = 'rafi m feroze'

PROVISION_ENABLE_REQUEST_STATUS = [
    REQUEST_STATUS_APPROVED, REQUEST_STATUS_LEGACY_APPROVED]

"""
Create a new user for provider  @ http://localhost:8000/admin/auth/user/
  user p001 with password p123  (id set to 15 in migrations,
  so ensure this id is relevant)

Create Crams user, with user id p001

Update Provider and set user for
  Nectar @ http://localhost:8000/admin/api/provider/9/
  select crams user created above 'p001'
  set user active
  ensure provider is set to NeCTAR
  save
  login to API with user p001

"""


def fetch_project_provision_list_for_provider(project_obj, provider_obj):
    """Fetch project provision list for provider."""
    return project_obj.linked_provisiondetails.filter(
        provision_details__provider=provider_obj
    )


def new_provision_detail(current_user, status=ProvisionDetails.SENT):
    return ProvisionDetails.objects.create(
        provider=current_user.provider,
        created_by=current_user,
        updated_by=current_user,
        status=status)

    ##############################################
    # API 1 :  List Products for provisioning    #
    ##############################################


class ProvisionProjectSerializer(ReadOnlyProjectSerializer):
    """class ProvisionProjectSerializer."""
    def filter_provision_project(self, project_obj):
        """

        :param project_obj:
        :return:
        """
        self._setActionState()
        context_request = self.cramsActionState.rest_request
        current_user = context_request.user

        ret_list = []
        if not Provider.is_provider(current_user):
            return ret_list

        status_filter_set = ProvisionDetails.READY_TO_SEND_SET

        new_only = context_request.query_params.get('new_request', None)
        if not new_only:
            status_filter_set = \
                status_filter_set.union(ProvisionDetails.SET_OF_SENT)

        provider_provision_details = fetch_project_provision_list_for_provider(
            project_obj, current_user.provider)
        if not provider_provision_details.exists():  # new Project
            project_provision = ProjectProvisionDetails(project=project_obj)
            new_project_pd = new_provision_detail(
                current_user, status=ProvisionDetails.SENT)
            project_provision.provision_details = new_project_pd
            project_provision.save()
            status_filter_set.union(ProvisionDetails.SENT)

        query_set = provider_provision_details.filter(
            provision_details__status__in=status_filter_set)
        for pp in query_set.all():
            pd = pp.provision_details
            if pd.status == ProvisionDetails.POST_PROVISION_UPDATE:
                pd.status = ProvisionDetails.POST_PROVISION_UPDATE_SENT
                pd.save()
            ret_list.append(ProvisionDetailsSerializer(pd).data)
        return ret_list

    def filter_requests(self, project_obj):
        """filter requests."""
        self._setActionState()
        context_request = self.cramsActionState.rest_request
        current_user = context_request.user

        ret_list = []
        if not Provider.is_provider(current_user):
            return ret_list

        query_params = context_request.query_params
        request_id = query_params.get('request_id', None)
        if request_id:
            # , parent_request__isnull=True)
            requests = project_obj.requests.filter(id=request_id)
        else:
            requests = project_obj.requests.filter(parent_request__isnull=True)

        requests = requests.filter(
            request_status__code=REQUEST_STATUS_APPROVED)

        valid_provider = fetch_active_provider_object_for_user(current_user)
        provider_filter = Q(
            compute_requests__compute_product__provider=valid_provider) | Q(
            storage_requests__storage_product__provider=valid_provider)

        for req in requests.filter(provider_filter):
            req_json = ProvisionRequestSerializer(
                req, context=self.context).data
            if req_json:
                if ('compute_requests' in req_json and
                    len(req_json['compute_requests']) > 0) or \
                   ('storage_requests' in req_json and
                   len(req_json['storage_requests']) > 0):
                    ret_list.append(req_json)

        return ret_list


class ProvisionRequestSerializer(ReadOnlyCramsRequestSerializer):
    """class ProvisionRequestSerializer."""

    request_status = SlugRelatedField(
        many=False, read_only=True, slug_field='status')
    compute_requests = serializers.SerializerMethodField(
        method_name='filter_compute_requests')
    storage_requests = serializers.SerializerMethodField(
        method_name='filter_storage_requests')

    def _filter_common(self, baseQuerySet, getRepresentationFn):
        self._setActionState()
        context_request = self.cramsActionState.rest_request
        current_user = context_request.user

        ret_list = []
        if not Provider.is_provider(current_user):
            return ret_list

        query_filter = Q(provision_details__isnull=True) | Q(
            provision_details__status__in=ProvisionDetails.READY_TO_SEND_SET)
        new_only = context_request.query_params.get('new_request', None)
        if not new_only:
            query_filter = query_filter | Q(
                provision_details__status__in=ProvisionDetails.SET_OF_SENT)
        query_set = baseQuerySet.filter(query_filter)

        valid_provider = fetch_active_provider_object_for_user(current_user)
        if baseQuerySet.model == ComputeRequest:
            query_set = query_set.filter(
                compute_product__provider=valid_provider)
        elif baseQuerySet.model == StorageRequest:
            query_set = query_set.filter(
                storage_product__provider=valid_provider)

        for productRequest in query_set:
            ret_list.append(getRepresentationFn(productRequest))
            provision_details = productRequest.provision_details
            update_status = ProvisionDetails.POST_PROVISION_UPDATE
            update_sent_status = ProvisionDetails.POST_PROVISION_UPDATE_SENT
            if provision_details:
                if provision_details.status == update_status:
                    provision_details.status = update_sent_status
                    provision_details.save()
            else:
                # new Product Request
                # - Create new Sent Provision details for Product Request
                pd = new_provision_detail(current_user)
                productRequest.provision_details = pd
                productRequest.save()

        return ret_list

    def filter_compute_requests(self, request_obj):
        """filter compute requests."""
        def getRepresentationFn(computeRequest):
            """get representation fn."""
            product = computeRequest.compute_product
            return {
                'id': computeRequest.id,
                'product': {'id': product.id, 'name': product.name},
                'approved_instances': computeRequest.approved_instances,
                'approved_cores': computeRequest.approved_cores,
                'approved_core_hours': computeRequest.approved_core_hours
            }

        return self._filter_common(
            request_obj.compute_requests,
            getRepresentationFn)

    def filter_storage_requests(self, request_obj):
        """filter storage requests."""
        def getRepresentationFn(storageRequest):
            """get representation fn."""
            product = storageRequest.storage_product
            storage_type = product.storage_type
            return {
                'id': storageRequest.id,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'storage_type': {
                        'id': storage_type.id,
                        'storage_type': storage_type.storage_type},
                    'zone': {
                        'id': product.zone.id,
                        'name': product.zone.name}},
                'approved_quota': storageRequest.approved_quota,
            }

        return self._filter_common(
            request_obj.storage_requests,
            getRepresentationFn)


##############################################
#   API 2 :  Update Provisioning Result      #
##############################################
class UpdateOnlySerializer(serializers.Serializer):
    """class UpdateOnlySerializer."""

    def pprint(self, obj):
        """print."""
        if not hasattr(self, 'pp'):
            self.pp = pprint.PrettyPrinter(indent=4)  # For Debug
        self.pp.pprint(obj)

    def create(self, validated_data):
        """create."""
        raise ParseError('Create not allowed ')


class BaseProvisionSerializer(UpdateOnlySerializer):
    """class BaseProvisionSerializer."""

    id = serializers.IntegerField()

    def _init_empty(self, str, num):
        ret_dict = {}
        ret_dict['id'] = num
        return ret_dict

    def _init_from_id_data(self, id):
        ret_dict = {}
        ret_dict['id'] = id
        return ret_dict

    def validate(self, data):
        """validate."""
        if not id:
            raise ValidationError({'id': 'This field is required.'})
        return data

    def get_current_user(self):
        """get current user."""
        if self.context and 'request' in self.context:
            return self.context['request'].user
        raise ValidationError(
            {'message': '"context" object not found, \
            required to identify current user.'})

    def validate_user_is_provider(self):
        """validate user is provider."""
        current_user = self.get_current_user()
        if Provider.is_provider(current_user):
            return True
        raise ValidationError({'message': 'User is not a provider'})

    def validate_user_provisions_product(self, product):
        """validate user provisions product."""
        current_user = self.get_current_user()
        if Provider.is_provider(current_user) and \
                current_user.provider == product.provider:
            return True
        raise ValidationError(
            {'message': 'User is not a provider for product {}'.format(
                repr(product))})


class BaseProvisionMessageSerializer(BaseProvisionSerializer):
    """class BaseProvisionMessageSerializer."""

    message = serializers.CharField(
        max_length=999, allow_null=True, allow_blank=True, required=False)
    success = serializers.BooleanField()

    def _init_empty(self, str, num):
        ret_dict = super(BaseProvisionMessageSerializer,
                         self)._init_empty(str, num)
        ret_dict['message'] = str + 'message '
        ret_dict['success'] = True
        return ret_dict

    def _initFromBaseIdData(self, id):
        ret_dict = super(BaseProvisionMessageSerializer,
                         self)._init_from_id_data(id)
        ret_dict['message'] = None
        ret_dict['success'] = True
        return ret_dict

    def validate(self, data):
        """validate."""
        #        super(BaseProvisionProductSerializer, self).validate(data)
        if not data.success and not data.message:
            raise ValidationError(
                {'message': 'This field is required when success is false'})
        return data


class ComputeRequestProvisionSerializer(BaseProvisionMessageSerializer):
    """class ComputeRequestProvisionSerializer."""

    compute_product = PrimaryKeyLookupField(
        many=False, required=True, fields=[
            'id', 'name'], queryset=ComputeProduct.objects.all())

    def _init_empty(self, str, num):
        ret_dict = super(ComputeRequestProvisionSerializer,
                         self)._init_empty(str, num)
        ret_dict['compute_product'] = self.__getitem__(
            'compute_product').to_representation({'id': 1})
        return ret_dict

    def _initFromComputeRequestData(self, computeRequestData):
        if not computeRequestData:
            return None

        ret_dict = super(
            ComputeRequestProvisionSerializer,
            self)._initFromBaseIdData(
            computeRequestData.get(
                'id',
                None))
        computeProduct = computeRequestData.get('compute_product', None)
        if computeProduct:
            ret_dict['compute_product'] = self.__getitem__('compute_product') \
                .to_representation({'id': computeProduct.get('id', None)})
        return ret_dict

    def validate(self, data):
        """validate."""
        compute_product = data['compute_product']
        self.validate_user_provisions_product(
            get_compute_product_obj(compute_product))
        try:
            # self.instance will force save action to perform update
            self.instance = ComputeRequest.objects.get(pk=data['id'])

            if not self.instance.provision_details:
                raise ValidationError(
                    {'compute_request':
                        '{} , request {} was never sent for provisioning'
                     .format(repr(self.instance),
                             repr(self.instance.request))
                     })

            if self.instance.provision_details.status not in \
                    ProvisionDetails.SET_OF_SENT:
                raise ValidationError(
                    {'compute_request':
                        '{} cannot be updated, status not in sent'
                     .format(repr(self.instance))
                     })

            if self.instance.compute_product.id != compute_product['id']:
                raise ValidationError(
                    {'compute_request':
                        'Invalid Product (id = {}) for {}'
                     .format(repr(compute_product['id']),
                             repr(self.instance))
                     })

            if 'success' not in data:
                raise ValidationError({'success': 'Field value is required'})

        except ComputeRequest.DoesNotExist:
            raise ValidationError(
                {'compute_request': 'Compute Request not found for id {}'
                 .format(repr(data['id']))
                 })

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        """update."""
        provision_details = instance.provision_details
        success = validated_data['success']
        if success:
            provision_details.status = ProvisionDetails.PROVISIONED
        else:
            resend = validated_data.get('resend', False)
            if resend:
                provision_details.status = ProvisionDetails.RESEND_LATER
            else:
                provision_details.status = ProvisionDetails.FAILED
            provision_details.message = validated_data.get('message', None)

        provision_details.save()
        validated_data['update_success'] = True
        return validated_data


class StorageRequestProvisionSerializer(BaseProvisionMessageSerializer):
    """class StorageRequestProvisionSerializer."""

    storage_product = PrimaryKeyLookupField(
        many=False, required=True, fields=[
            'id', 'name'], queryset=StorageProduct.objects.all())

    def _init_empty(self, str, num):
        ret_dict = super(StorageRequestProvisionSerializer,
                         self)._init_empty(str, num)
        ret_dict['storage_product'] = self.__getitem__(
            'storage_product').to_representation({'id': 1})
        return ret_dict

    def _initFromStorageRequestData(self, storageRequestData):
        if not storageRequestData:
            return None

        ret_dict = super(
            StorageRequestProvisionSerializer,
            self)._initFromBaseIdData(
            storageRequestData.get(
                'id',
                None))
        storageProduct = storageRequestData.get('storage_product', None)
        if storageProduct:
            ret_dict['storage_product'] = self.__getitem__(
                'storage_product').to_representation(
                {'id': storageProduct.get('id', None)})
        return ret_dict

    def validate(self, data):
        """validate."""
        storage_product = data['storage_product']
        self.validate_user_provisions_product(
            get_storage_product_obj(storage_product))
        try:
            # self.instance will force save action to perform update
            self.instance = StorageRequest.objects.get(pk=data['id'])
            if not self.instance.provision_details:
                raise ValidationError(
                    {'storage_request':
                        '{}  request {} was never sent for provisioning'
                        .format(repr(self.instance),
                                repr(self.instance.request))})

            if self.instance.provision_details.status not in \
                    ProvisionDetails.SET_OF_SENT:
                raise ValidationError(
                    {'storage_request':
                        '{} {} cannot be updated, status not in sent'.format(
                            repr(self.instance),
                            self.instance.provision_details.status)})

            if self.instance.storage_product.id != storage_product['id']:
                raise ValidationError(
                    {'storage_request':
                        'Invalid Product (id = {}) for {}'
                        .format(repr(storage_product['id']),
                                repr(self.instance))})

            if 'success' not in data:
                raise ValidationError({'success': 'Field value is required'})

        except StorageRequest.DoesNotExist:
            raise ValidationError(
                {'storage_request':
                    'Storage Request not found for id {}'
                    .format(repr(data['id']))})

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        """update."""
        provision_details = instance.provision_details
        success = validated_data['success']
        if success:
            provision_details.status = ProvisionDetails.PROVISIONED
        else:
            resend = validated_data.get('resend', False)
            if resend:
                provision_details.status = ProvisionDetails.RESEND_LATER
            else:
                provision_details.status = ProvisionDetails.FAILED

            provision_details.message = validated_data.get('message', None)

        provision_details.save()
        validated_data['update_success'] = True
        return validated_data


class UpdateProvisionRequestSerializer(BaseProvisionSerializer):
    """class UpdateProvisionRequestSerializer."""

    compute_requests = ComputeRequestProvisionSerializer(
        many=True, allow_null=True, required=False)
    storage_requests = StorageRequestProvisionSerializer(
        many=True, allow_null=True, required=False)

    def _init_empty(self, str, num):
        ret_dict = super(UpdateProvisionRequestSerializer,
                         self)._init_empty(str, num)
        ret_dict['compute_requests'] = [
            ComputeRequestProvisionSerializer()._init_empty(
                str + 'compute_request ', num)]
        ret_dict['storage_requests'] = [
            StorageRequestProvisionSerializer()._init_empty(
                str + 'storage_request ', num)]
        return ret_dict

    def _initFromRequestData(self, requestData):
        ret_dict = super(UpdateProvisionRequestSerializer,
                         self)._init_from_id_data(requestData.get('id', None))

        ret_dict['compute_requests'] = [
            ComputeRequestProvisionSerializer()
            ._initFromComputeRequestData(x)
            for x in requestData.get('compute_requests', [])]

        ret_dict['storage_requests'] = [
            StorageRequestProvisionSerializer()
            ._initFromStorageRequestData(x)
            for x in requestData.get('storage_requests', [])]

        return ret_dict

    def validate(self, data):
        """validate."""
        requestId = data.get('id', None)
        if not requestId:
            raise ValidationError(
                {'request': 'field "id" required, got ' + data})

        try:
            self.validate_user_is_provider()

            # self.instance will force save action to perform update
            self.instance = Request.objects.get(pk=requestId)
            if not self.instance:
                raise ValidationError(
                    {'request': 'Request with id {} does not belong to {}'
                     .format(repr(requestId), repr(self.instance))})
            if (self.instance.request_status.code not in
                    PROVISION_ENABLE_REQUEST_STATUS):
                raise ValidationError(
                    {'request':
                     'Request status is not Approved, \
                      provision update fail for {}'
                     .format(repr(self.instance))})

            # validate compute requests
            if 'compute_requests' in data:
                for inProductRequest in data['compute_requests']:
                    productRequestId = inProductRequest['id']
                    if not productRequestId:
                        raise ValidationError(
                            {'compute_request':
                             'field "id" required, got ' + inProductRequest})
                    existing_product_request = next(
                        (x for x in self.instance.compute_requests.all()
                         if x.id == productRequestId), None)
                    if not existing_product_request:
                        raise ValidationError(
                            {'compute_request':
                             'Compute Product Request with id {} \
                              does not belong to {}'
                             .format(repr(productRequestId,
                                     repr(self.instance)))})

            # validate storage requests
            if 'storage_requests' in data:
                for inProductRequest in data['storage_requests']:
                    productRequestId = inProductRequest['id']
                    if not productRequestId:
                        raise ValidationError(
                            {'storage_request':
                             'field "id" required, got ' + inProductRequest})
                    existing_product_request = next(
                        (x for x in self.instance.storage_requests.all()
                         if x.id == productRequestId), None)

                    if not existing_product_request:
                        raise ValidationError(
                            {'storage_request':
                             'Storage Product Request with id {} \
                              does not belong to {}'
                             .format(repr(productRequestId,
                                     repr(self.instance)))})

        except Request.DoesNotExist:
            raise ValidationError({'message': 'Request not found for id {}'
                                   .format(repr(requestId))})

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        """update."""
        # process compute request provisioning result
        in_compute_requests = validated_data.pop('compute_requests', [])
        out_compute_requests = []
        validated_data['compute_requests'] = out_compute_requests
        for inComputeRequest in in_compute_requests:
            productRequestSerializer = ComputeRequestProvisionSerializer(
                data=inComputeRequest, context=self.context)
            productRequestSerializer.is_valid(raise_exception=True)
            out_compute_requests.append(
                productRequestSerializer.save(request=instance))

        # process storage request provisioning result
        in_storage_requests = validated_data.pop('storage_requests', [])
        out_storage_requests = []
        validated_data['storage_requests'] = out_storage_requests
        for inStorageRequest in in_storage_requests:
            productRequestSerializer = StorageRequestProvisionSerializer(
                data=inStorageRequest, context=self.context)
            productRequestSerializer.is_valid(raise_exception=True)
            out_storage_requests.append(
                productRequestSerializer.save(request=instance))

        validated_data[
            'new_request_status'] = self._updateRequestStatus(instance)

        return validated_data

    @transaction.atomic
    def _updateRequestStatus(self, instance):

        if not instance:
            raise ValidationError(
                {'Severe Error, Contact Support':
                 'update request status failed, no existing \
                  instance passed in UpdateProvisionRequestSerializer'})

        status_code_to_update = REQUEST_STATUS_PROVISIONED
        for cpr in instance.compute_requests.all():
            if not (cpr.provision_details and cpr.provision_details.status ==
                    ProvisionDetails.PROVISIONED):
                status_code_to_update = None
                break

        if status_code_to_update:
            for spr in instance.storage_requests.all():
                if not (spr.provision_details and
                        spr.provision_details.status ==
                        ProvisionDetails.PROVISIONED):
                    status_code_to_update = None
                    break

        if status_code_to_update:
            context = dict()
            context['request'] = self.context['request']

            context[OVERRIDE_READONLY_DATA] = {
                'request_status': status_code_to_update,
                DO_NOT_OVERRIDE_PROVISION_DETAILS: True
            }
            newRequest = CramsRequestSerializer(
                instance, data={}, partial=True, context=context)
            newRequest.is_valid(raise_exception=True)
            newRequest.save()
            return status_code_to_update

        return instance.request_status.code


class UpdateProvisionProjectSerializer(BaseProvisionMessageSerializer):
    """class UpdateProvisionProjectSerializer."""

    requests = UpdateProvisionRequestSerializer(many=True)
    project_ids = ProjectIDSerializer(many=True, read_only=False)

    def _init_empty(self, str, num):
        ret_dict = super(UpdateProvisionProjectSerializer,
                         self)._init_empty(str, num)
        ret_dict['requests'] = [
            UpdateProvisionRequestSerializer()._init_empty(
                str + 'request ', num)]
        ret_dict['project_ids'] = [
            ProjectIDSerializer()._init_empty(str + 'project_id ', num)]
        return ret_dict

    def _init_from_project_data(self, projectData):
        ret_dict = super(UpdateProvisionProjectSerializer,
                         self)._initFromBaseIdData(projectData.get('id', None))
        ret_dict['requests'] = [UpdateProvisionRequestSerializer()
                                ._initFromRequestData(x)
                                for x in projectData.get('requests', [])]
        ret_dict['project_ids'] = [ProjectIDSerializer()
                                   ._init_from_project_id_data(x)
                                   for x in projectData.get('project_ids', [])]
        return ret_dict

    def validate(self, data):
        """validate."""
        projectId = data.get('id', None)
        if not projectId:
            raise ValidationError(
                {'project': 'field "id" required, got ' + data})
        try:
            # self.instance will force save action to perform update
            self.instance = Project.objects.get(pk=projectId)
            self.project_provision_list = \
                fetch_project_provision_list_for_provider(
                    self.instance, self.get_current_user().provider)
            if not self.project_provision_list.exists():
                raise ValidationError(
                    'id: project not in sent for provisioning status')

        except Project.DoesNotExist:
            raise ValidationError({'message': 'Project not found for id {}'
                                   .format(repr(projectId))})

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        """update."""
        self._updateProjectProvision(instance, validated_data)

        for projIdentifier in validated_data['project_ids']:
            existingProjectId = next((x for x in instance.project_ids.all(
            ) if x.system.id == projIdentifier['system']['id']), None)
            if not existingProjectId:
                idSerializer = ProjectIDSerializer(
                    data=projIdentifier, context=self.context)
                idSerializer.is_valid(raise_exception=True)
                idSerializer.save(project=instance)
                projIdentifier['update_success'] = True

        inRequests = validated_data.pop('requests', [])
        outRequests = []
        validated_data['requests'] = outRequests
        for inRequest in inRequests:
            requestSerializer = UpdateProvisionRequestSerializer(
                data=inRequest, context=self.context)
            requestSerializer.is_valid(raise_exception=True)
            outRequests.append(requestSerializer.save(project=instance))

        validated_data['success'] = True  # All updates successful
        return validated_data

    # noinspection PyUnusedLocal
    def _updateProjectProvision(self, instance, validated_data):
        project_provision_details = self.project_provision_list.first()

        if project_provision_details:
            provision_details = project_provision_details.provision_details
            success = validated_data.get('success', False)
            if success:
                provision_details.status = ProvisionDetails.PROVISIONED
            else:
                resend = validated_data.get('resend', False)
                if resend:
                    provision_details.status = ProvisionDetails.RESEND_LATER
                else:
                    provision_details.status = ProvisionDetails.FAILED

            message = validated_data.get('message', None)
            if message:
                provision_details.message = message
            provision_details.save()

            return success

        return False
