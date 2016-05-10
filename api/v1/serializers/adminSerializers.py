# coding=utf-8
"""Admin Serializers."""
from api.v1.serializers.requestSerializers import ComputeRequestSerializer
from api.v1.serializers.requestSerializers import CramsRequestSerializer
from api.v1.serializers.requestSerializers import StorageRequestSerializer
from api.v1.serializers.utilitySerializers import ProjectAdminField
from api.v1.serializers.utilitySerializers import UpdateOnlyModelSerializer
from api.v1.serializers.utils import FieldsRequiredValidator
from api.v1.serializers.utils import validate_dry_principle
from api.v1.serializers.lookupSerializers import FundingBodySerializer

from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework.serializers import SlugRelatedField

from crams.DBConstants import REQUEST_STATUS_APPROVED
from crams.DBConstants import REQUEST_STATUS_DECLINED
from crams.DBConstants import REQUEST_STATUS_LEGACY_APPROVED
from crams.DBConstants import REQUEST_STATUS_LEGACY_DECLINED
from crams.DBConstants import REQUEST_STATUS_SUBMITTED
from crams.DBConstants import REQUEST_STATUS_UPDATE_OR_EXTEND
from crams.DBConstants import REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED
from crams.models import Request
from api.v1.APIConstants import OVERRIDE_READONLY_DATA

__author__ = 'rafi m feroze'


ADMIN_ENABLE_REQUEST_STATUS = [
    REQUEST_STATUS_SUBMITTED, REQUEST_STATUS_UPDATE_OR_EXTEND]


class DeclineRequestModelSerializer(UpdateOnlyModelSerializer):
    """DeclineRequestModelSerializer."""

    project = ProjectAdminField(many=False, read_only=True)
    request_status = SlugRelatedField(
        many=False, read_only=True, slug_field='status')

    class Meta(object):
        """Meta for class DeclineRequestModelSerializer."""

        model = Request
        fields = ('id', 'approval_notes', 'project', 'request_status')
        read_only_fields = ('request_status', 'project')

    def update(self, instance, validated_data):
        """update.

        :param instance:
        :param validated_data:
        :return: :raise ParseError:
        """
        update_data = {}
        update_data['approval_notes'] = validated_data.get(
            'approval_notes', None)

        context = {}
        context['request'] = self.context['request']

        # sets the declined status based on the current request status
        if instance.request_status.code == 'E':
            # request_status is read_only, cannot be passed in update_data
            context[OVERRIDE_READONLY_DATA] = {
                'request_status': REQUEST_STATUS_DECLINED}
        elif instance.request_status.code == 'X':
            context[OVERRIDE_READONLY_DATA] = {
                'request_status': REQUEST_STATUS_UPDATE_OR_EXTEND_DECLINED}
        elif instance.request_status.code == 'L':
            context[OVERRIDE_READONLY_DATA] = {
                'request_status': REQUEST_STATUS_LEGACY_DECLINED}
        else:
            raise ParseError(
                'Can not decline request when the request_status is: ' +
                str(instance.request_status))

        new_request = CramsRequestSerializer(
            instance, data=update_data, partial=True, context=context)
        new_request.is_valid(raise_exception=True)
        return new_request.save()


class ApproveCompReqValid(FieldsRequiredValidator):
    """class ApproveCompReqValid."""

    @classmethod
    def get_fields_required(cls):
        """get Required fields.

        :return:
        """
        return ['approved_instances', 'approved_cores', 'approved_core_hours']

    @classmethod
    def get_fields_unchanged(cls):
        """getFieldsUnchanged.

        :return:
        """
        return [
            'instances', 'cores', 'core_hours', {
                'compute_product': ['id']}]


class ApproveStorReqValid(FieldsRequiredValidator):
    """class ApproveStorReqValid."""

    @classmethod
    def get_fields_required(cls):
        """getFieldsRequired.

        :return:
        """
        return ['approved_quota']

    @classmethod
    def get_fields_unchanged(cls):
        """get Fields Unchanged.

        :return:
        """
        return []  # issue 822/ task 823  'quota', {'storage_product': ['id']}]


class ApproveRequestModelSerializer(UpdateOnlyModelSerializer):
    """ApproveRequestModelSerializer."""

    project = ProjectAdminField(many=False, read_only=True)
    request_status = SlugRelatedField(
        many=False, read_only=True, slug_field='status')
    compute_requests = ComputeRequestSerializer(
        many=True, read_only=False, validators=[
            ApproveCompReqValid()])
    storage_requests = StorageRequestSerializer(
        many=True, read_only=False, validators=[
            ApproveStorReqValid()])
    funding_body = serializers.SerializerMethodField(method_name='get_fbody')

    class Meta(object):
        """meta for class ApproveRequestModelSerializer."""

        model = Request
        fields = (
            'id',
            'funding_body',
            'compute_requests',
            'storage_requests',
            'approval_notes',
            'request_status',
            'start_date',
            'end_date',
            'project')
        read_only_fields = ('funding_body', 'request_status', 'start_date',
                            'end_date', 'project')

    def get_fbody(self, request_obj):
        fb = request_obj.funding_scheme.funding_body
        return FundingBodySerializer(fb).data

    def validate(self, data):
        """validate.

        :param data:
        :return:
        """
        validate_dry_principle(self, ApproveCompReqValid.get_fields_unchanged(
        ), 'compute_requests', 'Approver')
        validate_dry_principle(self, ApproveStorReqValid.get_fields_unchanged(
        ), 'storage_requests', 'Approver')
        return data

    def update(self, instance, validated_data):
        """Update.

        :param instance:
        :param validated_data:
        :return: :raise ParseError:
        """
        update_data = {}
        update_data['approval_notes'] = validated_data.get(
            'approval_notes', None)
        update_data['compute_requests'] = validated_data.get(
            'compute_requests', None)
        # Storage request has nested classes (zone, product etc) that do not
        # use PrimaryKeyLookup, hence require initial_data to ensure id is
        # passed down
        update_data['storage_requests'] = self.initial_data.get(
            'storage_requests', None)

        context = {}
        context['request'] = self.context['request']
        # only approve where request status code is 'E' or 'X'
        # noinspection PyPep8
        if instance.request_status.code == 'E' or \
           instance.request_status.code == "X":
            # request_status is read_only, cannot be passed in update_data
            context[OVERRIDE_READONLY_DATA] = {
                'request_status': REQUEST_STATUS_APPROVED}
        elif instance.request_status.code == 'L':
            context[OVERRIDE_READONLY_DATA] = {
                'request_status': REQUEST_STATUS_LEGACY_APPROVED}
        else:
            raise ParseError(
                'Can not approve request when the request_status is: ' +
                str(instance.request_status))

        new_request = CramsRequestSerializer(
            instance, data=update_data, partial=True, context=context)
        new_request.is_valid(raise_exception=True)
        return new_request.save()
