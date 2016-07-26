# coding=utf-8
"""Lookup Serializers."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from crams.models import AllocationHome
from crams.models import ComputeProduct
from crams.models import ContactRole
from crams.models import FORCode
from crams.models import FundingBody
from crams.models import FundingScheme
from crams.models import GrantType
from crams.models import ProjectIDSystem
from crams.models import Provider
from crams.models import Question
from crams.models import RequestStatus
from crams.models import StorageProduct
from crams.models import StorageType
from crams.models import Zone


User = get_user_model()


class QuestionSerializer(serializers.ModelSerializer):
    """class QuestionSerializer."""

    class Meta(object):
        """metaclass."""

        model = Question
        field = ('id', 'key', 'question_type', 'question')
        read_only_fields = ('id', 'question_type', 'question')


class ProviderSerializer(serializers.ModelSerializer):
    """class ProviderSerializer."""

    class Meta(object):
        """metaclass."""

        model = Provider
        fields = ('id', 'name', 'active')
        # read_only_fields = ('id', 'name')


class RequestStatusSerializer(serializers.ModelSerializer):
    """class RequestStatusSerializer."""

    class Meta(object):
        """metaclass."""

        model = RequestStatus
        fields = ('id', 'code', 'status')


class FundingSchemeSerializer(serializers.ModelSerializer):
    """class FundingSchemeSerializer."""

    class Meta(object):
        """metaclass."""

        model = FundingScheme
        fields = ('id', 'funding_scheme')


class FundingBodySerializer(serializers.ModelSerializer):
    """class FundingBodySerializer."""

    class Meta(object):
        """metaclass."""

        model = FundingBody
        fields = ('id', 'name')
        read_only_fields = ('id', 'name')


class ComputeProductSerializer(serializers.ModelSerializer):
    """class ComputeProductSerializer."""

    funding_body = FundingBodySerializer(many=False, read_only=True)
    provider = ProviderSerializer(many=False, read_only=True)

    class Meta(object):
        """metaclass."""

        model = ComputeProduct
        fields = ('id', 'name', 'funding_body', 'provider')
        read_only_fields = ('funding_body', 'provider')


class StorageTypeSerializer(serializers.ModelSerializer):
    """class StorageTypeSerializer."""

    class Meta(object):
        """metaclass."""

        model = StorageType
        fields = ('id', 'storage_type')


class ZoneSerializer(serializers.ModelSerializer):
    """class ZoneSerializer."""

    class Meta(object):
        """metaclass."""

        model = Zone
        fields = ('id', 'name')


class StorageProductZoneOnlySerializer(serializers.ModelSerializer):
    """class StorageProductZoneOnlySerializer."""

    storage_type = StorageTypeSerializer(many=False, read_only=True)
    zone = ZoneSerializer(many=False, read_only=True)
    name = serializers.CharField(required=False)

    class Meta(object):
        """metaclass."""

        model = StorageProduct
        fields = ('id', 'name', 'storage_type', 'zone')


class StorageProductSerializer(serializers.ModelSerializer):
    """class StorageProductSerializer."""

    storage_type = StorageTypeSerializer(many=False, read_only=True)

    funding_body = FundingBodySerializer(many=False, read_only=True)

    provider = ProviderSerializer(many=False, read_only=True)

    zone = ZoneSerializer(many=False, read_only=True)

    name = serializers.CharField(required=False)

    class Meta(object):
        """metaClass."""

        model = StorageProduct
        fields = ('id', 'name', 'storage_type',
                  'funding_body', 'provider', 'zone')


class GrantTypeSerializer(serializers.ModelSerializer):
    """class GrantTypeSerializer."""

    class Meta(object):
        """metaclass."""

        model = GrantType
        fields = ('id', 'description')


class ProjectIDSystemSerializer(serializers.ModelSerializer):
    """class ProjectIDSystemSerializer."""

    class Meta(object):
        """metaclass."""

        model = ProjectIDSystem
        field = ('id', 'system')


class ContactRoleSerializer(serializers.ModelSerializer):
    """class ContactRoleSerializer."""

    class Meta(object):
        """metaclass."""

        model = ContactRole
        field = ('id', 'name')


class FORCodeSerializer(serializers.ModelSerializer):
    """class FORCodeSerializer."""

    class Meta(object):
        """metaclass."""

        model = FORCode
        fields = ('id', 'code', 'description')


class AllocationHomeSerializer(serializers.ModelSerializer):
    """class AllocationHomeSerializer."""

    class Meta(object):
        """metaclass."""

        model = AllocationHome
        fields = ('id', 'code', 'description')


class UserSerializer(serializers.ModelSerializer):
    """class UserSerializer."""

    class Meta(object):
        """metaclass."""

        model = User
        fields = ('first_name', 'last_name', 'email')  # , 'auth_token')
