# coding=utf-8
"""
Crams Models
"""
from django.db import models
from account.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework.authtoken.models import Token

import datetime


class CramsToken(Token):
    """
    CramsToken Model
    """
    ks_roles = models.TextField(null=True, blank=True)


class CramsCommon(models.Model):
    """
    CramsCommon Model
    """
    creation_ts = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    last_modified_ts = models.DateTimeField(
        auto_now=True,
        editable=False
    )
    created_by = models.ForeignKey(
        User, related_name="%(class)s_created_by", blank=True, null=True)
    updated_by = models.ForeignKey(
        User, related_name="%(class)s_updated_by", blank=True, null=True)

    class Meta:
        abstract = True


class UserEvents(CramsCommon):
    """
    UserEvents Model
    """
    event_message = models.TextField()


class ContactRole(models.Model):
    """
    ContactRole Model
    """
    name = models.CharField(
        max_length=100, unique=True
    )

    def __str__(self):
        return '{}'.format(self.name)


class Contact(models.Model):
    """
    Contact Model
    """
    title = models.CharField(
        max_length=50, blank=True, null=True
    )

    given_name = models.CharField(
        max_length=200, blank=True, null=True
    )

    surname = models.CharField(
        max_length=200, blank=True, null=True
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=50, blank=True, null=True
    )

    organisation = models.CharField(
        max_length=200, blank=True, null=True
    )

    def __str__(self):
        return '{0} {1} {2} {3}'.format(
            self.id, self.title, self.given_name, self.surname)


class Provider(CramsCommon):
    """
    Provider Model
    """
    name = models.CharField(max_length=200, unique=False)
    crams_user = models.OneToOneField(User, blank=True, null=True)
    start_date = models.DateField(auto_now_add=True, editable=False)
    active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    @classmethod
    def is_provider(cls, userobj):
        """
        is user a provider
        :param userobj:
        :return: :raise Exception:
        """
        if isinstance(userobj, User):
            if userobj.is_active:
                return hasattr(userobj, 'provider')
            raise Exception('User is not an active Provider')
        raise Exception('User object expected got {}'.format(repr(userobj)))

    def get_status_str(self):
        """

        get status as string
        :return:
        """
        if not self.active:
            return 'inActive'
        return 'current'

    def __str__(self):
        return '{}'.format(self.name)


class ProvisionDetails(CramsCommon):
    """
    ProvisionDetails Model
    The status flow is
    - From Nothing to Sent
    - From Sent to Provisioned or Failed
    - From Provisioned to Updated
    - From Failed to Updated
    - From Updated to Update Sent
    - From Update Sent to Provisioned or Failed
    """
    SENT = 'S'
    PROVISIONED = 'P'
    POST_PROVISION_UPDATE = 'U'
    POST_PROVISION_UPDATE_SENT = 'X'
    FAILED = 'F'
    SET_OF_SENT = [SENT, POST_PROVISION_UPDATE_SENT]
    STATUS_CHOICES = ((SENT, 'Sent'), (PROVISIONED, 'Provisioned'),
                      (FAILED, 'Failed'), (POST_PROVISION_UPDATE, 'Updated'),
                      (POST_PROVISION_UPDATE_SENT, 'Update Sent'), )
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=SENT)
    provider = models.ForeignKey(Provider, related_name='provisioned_requests')
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{}. {} : {}'.format(self.id, self.status, self.message)


class ProvisionableItem(models.Model):
    """
    ProvisionableItem Model
    """
    provision_details = models.OneToOneField(
        ProvisionDetails, blank=True, null=True, related_name='%(class)s')

    class Meta:
        abstract = True

    def get_provider(self):
        """
        get provider
        :raise NotImplementedError:
        """
        raise NotImplementedError(
            'Get Provider not implemented for abstract Product Request model')


class ProjectIDSystem(models.Model):
    """
    ProjectIDSystem Model
    """
    system = models.CharField(
        max_length=100
    )

    def __str__(self):
        return '{}'.format(self.system)


class FundingBody(models.Model):
    """
    FundingBody Model
    """
    name = models.CharField(
        max_length=200
    )

    email = models.EmailField()

    def __str__(self):
        return '{} - {}'.format(self.name, self.email)


class FundingScheme(models.Model):
    """
    FundingScheme Model
    """
    funding_scheme = models.CharField(
        max_length=200
    )

    funding_body = models.ForeignKey(
        FundingBody, related_name='funding_schemes')

    def __str__(self):
        return '{} {}'.format(self.funding_body.name, self.funding_scheme)


class Project(CramsCommon):
    """
    Project Model
    """
    # for project versioning, if parent_project is null which means it's a
    # latest project request
    parent_project = models.ForeignKey('Project', null=True, blank=True)

    title = models.CharField(
        max_length=255
    )

    description = models.CharField(
        max_length=255
    )

    notes = models.TextField(
        null=True,
        blank=True,
        max_length=1024
    )

    def __str__(self):
        if self.parent_project:
            return '{}.{} - (Parent) {}'.format(self.id,
                                                self.title,
                                                self.parent_project.id)
        else:
            return '{}.{}'.format(self.id, self.title)


class ProjectContact(models.Model):
    """
    ProjectContact Model
    """
    project = models.ForeignKey(Project, related_name='project_contacts')
    contact = models.ForeignKey(Contact, related_name='project_contacts')
    contact_role = models.ForeignKey(
        ContactRole, related_name='project_contacts')


class ProjectProvisionDetails(models.Model):
    """
    ProjectProvisionDetails Model
    """
    project = models.ForeignKey(
        Project, related_name='linked_provisiondetails')
    provision_details = models.ForeignKey(
        ProvisionDetails, related_name='linked_projects')


class ProjectID(models.Model):
    """
    ProjectID Model
    """
    identifier = models.CharField(max_length=64)

    project = models.ForeignKey(Project, related_name='project_ids')

    system = models.ForeignKey(ProjectIDSystem, related_name='project_ids')

    def get_provider(self):
        """
        get_provider
        :return:
        """
        if self.provision_details:
            return self.provision_details.provider
        return None

    def __str__(self):
        return '{} {}'.format(self.identifier, self.project)


class RequestStatus(models.Model):
    """
    RequestStatus Model
    """
    code = models.CharField(
        max_length=50
    )

    status = models.CharField(
        max_length=100
    )

    def __str__(self):
        return '{} {} {}'.format(self.id, self.code, self.status)


class Request(CramsCommon):
    """
    Request Model
    """
    # For versioning
    parent_request = models.ForeignKey(
        'Request', null=True, blank=True, related_name='history')

    project = models.ForeignKey(Project, related_name='requests')

    request_status = models.ForeignKey(RequestStatus, related_name='requests')

    funding_scheme = models.ForeignKey(FundingScheme, related_name='requests')

    start_date = models.DateField(
        default=datetime.date.today
    )
    end_date = models.DateField()

    approval_notes = models.TextField(
        null=True,
        blank=True,
        max_length=1024
    )

    def __str__(self):
        return '{}.{}'.format(self.id, self.project.title)


class ProductCommon(models.Model):
    """
    ProductCommon Model
    """
    name = models.CharField(max_length=200)

    funding_body = models.ForeignKey(FundingBody, related_name='%(class)s')

    provider = models.ForeignKey(Provider, related_name='%(class)s')

    class Meta:
        abstract = True

    def __str__(self):
        return '{} {}'.format(self.id, self.name)


class ComputeProduct(ProductCommon):
    """
    ComputeProduct Model
    """
    pass


class ComputeRequest(ProvisionableItem):
    """
    ComputeRequest Model
    """
    instances = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)]
    )

    approved_instances = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)]
    )

    cores = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)]
    )

    approved_cores = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1)]
    )

    core_hours = models.IntegerField(
        default=744,
        validators=[MinValueValidator(1)]
    )

    approved_core_hours = models.IntegerField(
        default=744,
        validators=[MinValueValidator(1)]
    )

    compute_product = models.ForeignKey(
        ComputeProduct, related_name='compute_requests')

    request = models.ForeignKey(Request, related_name='compute_requests')

    def get_provider(self):
        """
        get_provider

        :return:
        """
        return self.compute_product.provider

    def __str__(self):
        return '{}/{}: {} {} {}'.format(self.id,
                                        self.request.id,
                                        self.instances,
                                        self.cores,
                                        self.core_hours)


class FORCode(models.Model):
    """
    FORCode Model
    """
    code = models.CharField(
        max_length=50
    )

    description = models.CharField(
        max_length=200
    )

    def __str__(self):
        return '{} {}'.format(self.code, self.description)


class Domain(models.Model):
    """
    Domain Model
    """
    percentage = models.FloatField(
        default=0.0
    )

    project = models.ForeignKey(Project, related_name='domains')

    for_code = models.ForeignKey(FORCode, related_name='domains')

    def __str__(self):
        return '{} {} {}'.format(
            self.project.title,
            self.for_code.code,
            self.percentage)


class SupportedInstitution(models.Model):
    """
    SupportedInstitution Model
    """
    institution = models.CharField(
        max_length=200
    )

    project = models.ForeignKey(Project, related_name='institutions')

    def __str__(self):
        return '{}'.format(self.institution)


class Publication(models.Model):
    """
    Publication Model
    """
    reference = models.CharField(
        max_length=255
    )

    project = models.ForeignKey(Project, related_name='publications')

    def __str__(self):
        return '{}'.format(self.reference)


class GrantType(models.Model):
    """
    GrantType Model
    """
    description = models.CharField(
        max_length=200
    )

    def __str__(self):
        return '{} {}'.format(self.id, self.description)


class Grant(models.Model):
    """
    Grant Model
    """
    project = models.ForeignKey(Project, related_name='grants')

    grant_type = models.ForeignKey(GrantType, related_name='grants')

    funding_body_and_scheme = models.CharField(
        blank=False,
        max_length=200
    )

    grant_id = models.CharField(
        blank=True,
        max_length=200
    )

    start_year = models.IntegerField(
        blank=False,
        default=datetime.datetime.now().year,
        validators=[MinValueValidator(1970), MaxValueValidator(3000)],
        error_messages={
            'min_value': 'Please input a year between 1970 ~ 3000',
            'max_value': 'Please input a year between 1970 ~ 3000'}
    )

    total_funding = models.FloatField(
        blank=True,
        default=0.0
    )

    def __str__(self):
        return '{} {} {}'.format(
            self.grant_type,
            self.funding_body,
            self.start_year)


class StorageType(models.Model):
    """
    StorageType Model
    """
    storage_type = models.CharField(
        max_length=100
    )

    def __str__(self):
        return '{}'.format(self.storage_type)


class Zone(models.Model):
    """
    Zone Model
    """
    name = models.CharField(max_length=64)
    description = models.TextField()

    def __str__(self):
        return '{}'.format(self.name)


class StorageProduct(ProductCommon):
    """
    StorageProduct Model
    """
    zone = models.ForeignKey(
        Zone, related_name='storage_products', null=True, blank=True)

    storage_type = models.ForeignKey(
        StorageType, related_name='storage_products')

    def __str__(self):
        return '{} - {}'.format(self.name, self.provider)


class StorageRequest(ProvisionableItem):
    """
    StorageRequest Model
    """
    quota = models.FloatField(
        default=0.0
    )

    approved_quota = models.FloatField(
        default=0.0
    )

    storage_product = models.ForeignKey(
        StorageProduct, related_name='storage_requests')

    request = models.ForeignKey(Request, related_name='storage_requests')

    def get_provider(self):
        """


        :return:
        """
        return self.storage_product.provider

    def __str__(self):
        return '{}/{}: {} {}'.format(self.id,
                                     self.request.id,
                                     self.storage_product.name,
                                     self.quota)


class Question(models.Model):
    """
    Question Model
    """
    key = models.CharField(
        max_length=50
    )

    question_type = models.CharField(
        max_length=200
    )

    question = models.CharField(
        max_length=200
    )

    def __str__(self):
        return '{} {} {}'.format(self.key, self.question_type, self.question)


class ComputeRequestQuestionResponse(models.Model):
    """
    ComputeRequestQuestionResponse Model
    """
    question_response = models.TextField(
        max_length=1024,
        blank=True
    )

    question = models.ForeignKey(
        Question, related_name='compute_question_responses')

    compute_request = models.ForeignKey(
        ComputeRequest, related_name='compute_question_responses')


class StorageRequestQuestionResponse(models.Model):
    """
    StorageRequestQuestionResponse Model
    """
    question_response = models.TextField(
        max_length=1024,
        blank=True
    )

    question = models.ForeignKey(
        Question, related_name='storage_question_responses')

    storage_request = models.ForeignKey(
        StorageRequest, related_name='storage_question_responses')


class ProjectQuestionResponse(models.Model):
    """
    ProjectQuestionResponse Model
    """
    question_response = models.TextField(
        max_length=1024,
        blank=True

    )

    question = models.ForeignKey(
        Question, related_name='project_question_responses')

    project = models.ForeignKey(
        Project, related_name='project_question_responses')


class RequestQuestionResponse(models.Model):
    """
    RequestQuestionResponse Model
    """
    question_response = models.TextField(
        max_length=1024,
        blank=True
    )

    question = models.ForeignKey(
        Question, related_name='request_question_responses')

    request = models.ForeignKey(
        Request, related_name='request_question_responses')


class Duration(models.Model):
    """
    Duration Model
    """
    duration = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    duration_label = models.CharField(
        max_length=50
    )

    def __str__(self):
        return '{} {}'.format(self.duration, self.duration_label)


class AllocationHome(models.Model):
    """
    Allocation Home
    """
    code = models.CharField(
        max_length=50
    )
    description = models.CharField(
        max_length=200
    )

    def __str__(self):
        return '{} {} {}'.format(self.id, self.code, self.description)
