# coding=utf-8
"""Utils."""

from abc import ABCMeta

from rest_framework.serializers import ValidationError

from crams_app.django_utils import get_model_field_value
from crams.api.v1.APIConstants import CLONE
from crams.api.v1.APIConstants import OVERRIDE_READONLY_DATA

__author__ = 'rafi m feroze'


class FieldsRequiredValidator(metaclass=ABCMeta):
    """class FieldsRequiredValidator."""

    @classmethod
    def get_fields_required(cls):
        """get required fields."""
        pass

    @classmethod
    def get_fields_unchanged(cls):
        """get fields unchanged"""
        pass

    def __call__(self, obj_dict):
        for field in self.get_fields_required():
            if field not in obj_dict:
                raise ValidationError({field: 'field is required'})


class CramsActionState(object):
    """class CramsActionState."""

    def __init__(self, parent_obj):
        self.error_message = None
        if not parent_obj:
            self.error_message = 'CramsActionState: invalid object'
            return

        self.existing_instance = parent_obj.instance
        self.is_update_action = self.existing_instance is not None
        self.is_create_action = not self.is_update_action
        self.is_partial_action = parent_obj.partial
        self.is_clone_action = False

        if not parent_obj.context or 'request' not in parent_obj.context:
            self.error_message = '"context" object not found, required to \
                                 identify current user.'
            return

        self.rest_request = parent_obj.context.get('request', None)

        self.override_data = parent_obj.context.get(OVERRIDE_READONLY_DATA,
                                                    None)
        if self.override_data:
            if CLONE in self.override_data:
                if not self.existing_instance:
                    self.error_message = 'existing_instance required for \
                                         Clone Action'
                    return
                else:
                    self.is_clone_action = True
                    self.is_update_action = False

        # noinspection PyPep8
        self.update_from_existing = self.is_partial_action or \
            self.is_clone_action


def validate_dry_principle(serializer_instance, fields_unchanged_list,
                           list_name_str, user_role_str):
    """validate dry principle.

    :param serializer_instance:
    :param fields_unchanged_list:
    :param list_name_str:
    :param user_role_str:
    :return: :raise ValidationError:
    """
    if not list_name_str:
        raise ValidationError(
            {'listNameStr / validate_DRY ': 'parameter cannot be null, ' +
                                            'contact Tech Support'})

    if not serializer_instance.instance:
        raise ValidationError({'{}'.format(
            repr(serializer_instance)): 'instance not found, contact ' +
                                        'Tech Support'})

    # Do not use the parsed validatedData, it does not contain id pk
    intial_data_list = serializer_instance.initial_data.get(list_name_str,
                                                            None)
    existing_instance_list = get_model_field_value(
        serializer_instance.instance, list_name_str).all()

    msg = None
    if not intial_data_list:
        if existing_instance_list:
            msg = '{} cannot remove existing {}'.format(
                user_role_str, list_name_str)
    elif not existing_instance_list:
        msg = '{} cannot add new {}'.format(user_role_str, list_name_str)
    elif len(intial_data_list) < len(existing_instance_list):
        msg = '{} cannot remove existing {}'.format(user_role_str,
                                                    list_name_str)
    elif len(intial_data_list) > len(existing_instance_list):
        msg = '{} cannot add new {}'.format(user_role_str,
                                            list_name_str)

    if msg:
        raise ValidationError({list_name_str: msg})

    existing_instance_map = {}
    for cr in existing_instance_list:
        existing_instance_map[cr.id] = cr

    def verify_fields():  # useful inner function
        """verify fields.

        :return: :raise ValidationError:
        """

        def recursive_verify(field_list, existing, in_data, parent_field_str):
            """recursive verify.

            :param field_list:
            :param existing:
            :param in_data:
            :param parent_field_str:
            :raise ValidationError:
            """
            for field in field_list:
                if isinstance(field, dict):
                    for k in field.keys():
                        model_instance = get_model_field_value(existing, k)
                        if not model_instance:
                            raise ValidationError(
                                {parent_field_str: '{} field not found in ' +
                                    'model {}'.format(k, type(existing))})
                        in_data_value = in_data.get(k, None)
                        if not in_data_value:
                            raise ValidationError(
                                {parent_field_str: '{} field required'.
                                    format(k)})
                        recursive_verify(
                            field.get(k),
                            model_instance,
                            in_data_value,
                            '{} {} (id: {})'.format(
                                parent_field_str,
                                k,
                                repr(
                                    model_instance.id)))
                else:
                    in_data_value = in_data.get(field, None)
                    if in_data_value:
                        if get_model_field_value(existing, field) \
                                != in_data_value:
                            # noinspection PyPep8
                            raise ValidationError(
                                {parent_field_str: '{} ' + 'value cannot be \
                                 changed by {} to {}'.format(field,
                                 user_role_str, repr(in_data_value))})

        return recursive_verify

    for in_data in intial_data_list:
        in_id = in_data.pop('id', None)
        if not in_id:
            raise ValidationError({list_name_str: 'id is required'})

        existing = existing_instance_map.pop(in_id, None)
        if not existing:
            raise ValidationError(
                {list_name_str: 'missing object with id {}'.
                    format(repr(in_id))})

        validator = verify_fields()
        validator(fields_unchanged_list, existing, in_data,
                  '{} (id: {} )'.format(list_name_str, repr(in_id)))
