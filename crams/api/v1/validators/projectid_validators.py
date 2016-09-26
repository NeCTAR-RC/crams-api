# coding=utf-8
"""
ProjectId Validators
"""
import copy
import abc

from django.utils.translation import ugettext_lazy as _
from django.db import models as django_models

from rest_framework import serializers
from rest_framework.exceptions import ParseError

from crams import settings
from crams import lang_utils
from crams import models as crams_models
from crams.api.v1.dataUtils import lookupData


def extract_project_id_save_args(project_id_data):
    ret_dict = copy.deepcopy(project_id_data)

    system_data = project_id_data.get('system')
    if not system_data:
        raise serializers.ValidationError(
            'Project Id ({}): System details is required'.format(
                project_id_data.get('identifier')))
    try:
        ret_dict['system_obj'] = lookupData.get_system_obj(system_data)
    except ParseError as e:
        raise serializers.ValidationError('Project Id ({}): {}'.format(
            ret_dict['identifier'], repr(e)))

    return ret_dict


class AbstractUniqueSystemProjectIDValidator(metaclass=abc.ABCMeta):
    message = _('ProjectID must be unique for a given system.')

    def __init__(self, queryset=None, message=None):
        self.queryset = queryset or crams_models.ProjectID.objects.all()
        self.message = message or self.message
        self.serializer_field = None

    @abc.abstractmethod
    def get_parent_project(self, serializer_field):
        """
        override this method to return a relevant project object, if any,
        :param serializer_field:
        :return:
        """
        return None

    def set_context(self, serializer_field):
        self.serializer_field = serializer_field

    def __call__(self, data):
        save_args = extract_project_id_save_args(data)
        self.validate_identifier_is_unique(save_args['identifier'],
                                           save_args['system_obj'])

    def validate_identifier_is_unique(self, identifier, system):
        """
        Identifier check should ignore existingInstance and related history
        - Checking on the current project is redundant, since update to
          parent_project field occurs after project_ids are created.

        :param identifier:
        :param system:
        :return:
        """
        qs = self.queryset.filter(identifier=identifier, system=system)
        parent_project = self.get_parent_project(self.serializer_field)
        if parent_project:
            if isinstance(parent_project, crams_models.Project):
                qs = qs.exclude(
                    django_models.Q(
                        project__parent_project=parent_project) |
                    django_models.Q(project=parent_project))
        if qs.exists():
            raise serializers.ValidationError(
                'Project Id ({}): exists, must be unique'.format(identifier))


class UniqueSystemProjectIDValidator(AbstractUniqueSystemProjectIDValidator):
    def __init__(self, project):
        super().__init__()
        self.project = project

    def get_parent_project(self, serializer_field):
        return self.project


class ValidateProjectIDPrefix(object):
    message = _('ProjectID identifier prefix invalid.')

    def __init__(self, message=None):
        self.message = message or self.message
        self.serializer_field = None

    def set_context(self, serializer_field=None):
        self.serializer_field = serializer_field

    def __call__(self, data):
        save_args = extract_project_id_save_args(data)
        system_obj = save_args['system_obj']
        identifier = save_args['identifier']

        invalid_prefix_list = \
            settings.PROJECT_SYSTEM_ID_INVALID_PREFIX_MAP.get(
                system_obj.system.lower())
        if invalid_prefix_list and \
                lang_utils.has_invalid_prefix(identifier.lower(),
                                              invalid_prefix_list):
            raise serializers.ValidationError(
                'Project Id ({}): cannot begin with '.format(
                    identifier, ' or '.join(invalid_prefix_list)))
