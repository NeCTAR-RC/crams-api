# coding=utf-8
"""utilitySerializers."""
import pprint

from crams.api.v1.dataUtils.lookupData import get_provider_obj
from crams.api.v1.serializers.lookupSerializers import ProviderSerializer
from crams.api.v1.serializers.utils import CramsActionState
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.relations import RelatedField

from crams.models import Question, ProvisionDetails
from crams.api.v1.APIConstants import DO_NOT_OVERRIDE_PROVISION_DETAILS
from crams.api.v1.APIConstants import OVERRIDE_READONLY_DATA
from crams.roleUtils import has_role_fb


class ActionStateModelSerializer(serializers.ModelSerializer):
    """class ActionStateModelSerializer."""

    def pprint(self, obj):
        """pprint.

        :param obj:
        """
        if not hasattr(self, 'pp'):
            self.pp = pprint.PrettyPrinter(indent=4)  # For Debug
        self.pp.pprint(obj)

    def _setActionState(self):
        if not hasattr(self, 'cramsActionState'):
            self.cramsActionState = CramsActionState(self)
            if self.cramsActionState.error_message:
                raise ValidationError(
                    'ActionStateModelSerializer: ' +
                    self.cramsActionState.error_message)

    def to_representation(self, instance):
        # make available CramsActionState object for 'get' operation
        self._setActionState()

        return super(ActionStateModelSerializer,
                     self).to_representation(instance)


class ProvisionDetailsSerializer(serializers.ModelSerializer):
    """class ProvisionDetailsSerializer."""

    provider = ProviderSerializer(many=False)
    SHOW_FAIL_MESSAGE = 'show_fail_message'

    class Meta(object):
        model = ProvisionDetails
        fields = ('id', 'status', 'message', 'provider')
        read_only_fields = ('provider')

    @classmethod
    def hide_error_msg_context(cls):
        return {cls.SHOW_FAIL_MESSAGE: False}

    @classmethod
    def show_error_msg_context(cls):
        return {cls.SHOW_FAIL_MESSAGE: True}

    @classmethod
    def build_context_obj(cls, user_obj, funding_body_obj=None):
        if has_role_fb(user_obj, funding_body_obj):
            return cls.show_error_msg_context()
        return cls.hide_error_msg_context()

    @classmethod
    def sanitize_provision_details_for_user(cls, provision_details_dict):
        if provision_details_dict.get('status') == ProvisionDetails.FAILED:
            provision_details_dict['status'] = ProvisionDetails.SENT
            provision_details_dict['message'] = None

    def to_representation(self, instance):
        data = super(ProvisionDetailsSerializer,
                     self).to_representation(instance)
        if self.context:
            if not self.context.get(self.SHOW_FAIL_MESSAGE, False):
                self.sanitize_provision_details_for_user(data)
        return data

    def validate(self, data):
        """validate.

        :param data:
        :return validated_data:
        """
        # self._setActionState()  #Do not use this now,
        # requires passing context everywhere this serializer
        # is called, phase 2 perhaps
        self.override_data = dict()
        if self.context:
            self.override_data = self.context.get(
                OVERRIDE_READONLY_DATA, None)

        if data['status'] in ProvisionDetails.SET_OF_SENT:
            parentProductRequest = ''
            if self.existing:
                if self.existing.compute_requests:
                    parentProductRequest = self.existing.compute_requests
                elif self.existing.storage_requests:
                    parentProductRequest = self.existing.storage_requests
            raise ValidationError({'Product Request ':
                                   '{} cannot be updated while being \
                                   provisioned'
                                   .format(repr(parentProductRequest))})

        return data

    def _get_new_provision_status(self, existing_status):

        if existing_status == ProvisionDetails.PROVISIONED:
            key = DO_NOT_OVERRIDE_PROVISION_DETAILS
            if self.override_data and self.override_data.get(key, False):
                pass
            else:
                return ProvisionDetails.POST_PROVISION_UPDATE

        return existing_status

    def create(self, validated_data):
        p_status = validated_data.get('status')

        validated_data['status'] = self._get_new_provision_status(p_status)

        providerDict = validated_data.pop('provider')
        providerName = providerDict['name']
        validated_data['provider'] = get_provider_obj({'name': providerName})

        return ProvisionDetails.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """

        :param instance:
        :param validated_data:
        :return:
        """
        raise ParseError('ProvisionDetails: Update not allowed, clone new ')


class UpdatableSerializer(object):
    """class UpdatableSerializer."""

    def update(self, instance, validated_data):
        """update.

        :param instance:
        :param validated_data:
        :return instance:
        """
        for f in self.model._meta.get_all_field_names():
            setattr(instance, f, validated_data.get(f, getattr(instance, f)))
        instance.save()
        return instance


class UpdateOnlyModelSerializer(serializers.ModelSerializer):
    """class UpdateOnlyModelSerializer."""

    def create(self, validated_data):
        """create.

        :param validated_data:
        """
        raise ParseError('Create not allowed ')


class ReadOnlyModelSerializer(UpdateOnlyModelSerializer):
    """class ReadOnlyModelSerializer."""

    def update(self, instance, validated_data):
        """update.

        :param instance:
        :param validated_data:
        """
        raise ParseError('Update not allowed ')


class PrimaryKeyLookupField(serializers.PrimaryKeyRelatedField):
    """class PrimaryKeyLookupField."""

    def __init__(self, *args, **kwargs):
        """init.

        :param *args:
        :param **kwargs:
        """
        # Don't pass the 'fields' arg up to the superclass
        # Grant._meta.get_all_field_names()
        self.fields = kwargs.pop('fields', ['id'])
        self.pkFields = kwargs.pop('keyFields', ['id'])
        self.model = None

        # make sure this is a model class, not a string
        model = kwargs.pop('model', None)
        if model:
            self.model = model

        # Instantiate the superclass normally
        super(PrimaryKeyLookupField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        """to internal value.

        :param data:
        :return data:
        """
        if len(self.pkFields) > 0:
            ret_dict = {}
            for k in self.pkFields:
                try:
                    ret_dict[k] = data[k]
                except Exception:
                    raise ParseError(
                        '{}: Field {} required'.format(self.label, k))
            return ret_dict

        return data

    def to_representation(self, value):
        """to representation.

        :param value:
        :return ret_dict:
        """
        if self.pk_field is not None:
            return self.pk_field.to_representation(value.pk)

        try:
            if self.model:
                instance = self.model.objects.get(pk=value.pk)
            else:
                if isinstance(value, dict):
                    instance = self.get_queryset().get(**value)
                else:
                    instance = self.get_queryset().get(pk=value.pk)

            ret_dict = {}
            if self.fields:
                for k in self.fields:
                    ret_dict[k] = getattr(instance, k)
            return ret_dict

        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=value.pk)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(value.pk).__name__)


class DynamicFieldsBaseSerializer(serializers.BaseSerializer):
    """class DynamicFieldsBaseSerializer.

    A BaseSerializer that takes an additional `fields` argument that
    controls which fields should be displayed dynamically at invocation
    """

    def __init__(self, *args, **kwargs):
        """init.

        :param *args:
        :param **kwargs:
        """
        # Don't pass the 'fields' arg up to the superclass
        self.displayFields = kwargs.pop('display', None)
        self.validateRequired = kwargs.pop('required', None)
        # Instantiate the superclass normally
        super(DynamicFieldsBaseSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, obj):
        """to representation.

        :param obj:
        :param ret_dict:
        """
        ret_dict = {}
        if self.displayFields:
            for k in self.displayFields:
                ret_dict[k] = getattr(obj, k)

        return ret_dict

    def to_internal_value(self, data):
        """to internal value.

        :param data:
        :param ret_dict:
        """
        ret_dict = {}
        required = self.validateRequired
        if not required:
            required = ['id']
        for k in required:
            # Perform the data validation.
            val = data.get(k, None)
            if not val:
                raise ValidationError({
                    k: 'This field is required.'
                })
            ret_dict[k] = val

        return ret_dict


# refactored From http://tinyurl.com/ohsgt4g
class DynamicLookupModelSerializer(serializers.ModelSerializer):
    """class DynamicLookupModelSerializer.

    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    class Meta(object):
        pass

    def __init__(self, *args, **kwargs):
        """init.

        :param *args:
        :param **kwargs:
        """
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)
        # make sure this is a model class, not a string
        model = kwargs.pop('model', None)
        self.validateRequired = kwargs.pop('required', None)

        if model:
            self.Meta.model = model

        # ensure this serializer is read only
        kwargs['read_only'] = True
        # Instantiate the superclass normally
        super(DynamicLookupModelSerializer, self).__init__(*args, **kwargs)

        if fields:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_internal_value(self, data):
        """to internal value.

        :param data:
        :return ret_dict:
        """
        ret_dict = {}
        required = self.validateRequired
        if not required:
            required = ['id']
        for k in required:
            # Perform the data validation.
            val = data.get(k, None)
            if not val:
                raise ValidationError({
                    k: 'This field is required.'
                })
            ret_dict[k] = val

        return ret_dict

    def to_representation(self, instance):
        """to representation.

        :param instance:
        :return ret_dict:
        """
        ret_dict = {}
        if self.fields:
            for k in self.fields:
                ret_dict[k] = getattr(instance, k)

        return ret_dict


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """class DynamicFieldsModelSerializer.

    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        """init.

        :param *args:
        :param **kwargs:
        """
        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        fields = self.context['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProjectAdminField(RelatedField):
    """class ProjectAdminField."""

    def to_representation(self, value):
        """to representation.

        :param value:
        :return dict:
        """
        ret_list = []
        for id in value.project_ids.all():
            ret_list.append({'system': id.system.system, 'id': id.identifier})

        return {'title': value.title, 'ids': ret_list, 'id': value.id}


class AbstractQuestionResponseSerializer(serializers.ModelSerializer):
    """class AbstractQuestionResponseSerializer."""

    question = PrimaryKeyLookupField(
        many=False,
        required=True,
        fields=[
            'key',
            'question'],
        keyFields=['key'],
        queryset=Question.objects.all())

    def create(self, validated_data):
        """create.

        :param validated_data:
        :return meta:
        """
        question_data = validated_data.pop('question', None)
        if question_data and 'key' in question_data:
            key = question_data['key']
            question = Question.objects.filter(key=key)
            if question:
                current_question = question[0]
                return self.Meta.model.objects.create(
                    question=current_question, **validated_data)
            else:
                raise ParseError('No question linked to {}'.format(key))
        else:
            raise ParseError('Question field required')

    class Meta(object):
        model = None
        fields = ('id', 'question_response', 'question')
