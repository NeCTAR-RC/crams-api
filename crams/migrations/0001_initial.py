# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('authtoken', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AllocationHome',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('code', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ComputeProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ComputeRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('instances', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=2)),
                ('approved_instances', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=2)),
                ('cores', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=2)),
                ('approved_cores', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=2)),
                ('core_hours', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=744)),
                ('approved_core_hours', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=744)),
                ('compute_product', models.ForeignKey(to='crams.ComputeProduct', related_name='compute_requests')),
            ],
        ),
        migrations.CreateModel(
            name='ComputeRequestQuestionResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('question_response', models.TextField(blank=True, max_length=1024)),
                ('compute_request', models.ForeignKey(to='crams.ComputeRequest', related_name='compute_question_responses')),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(null=True, blank=True, max_length=50)),
                ('given_name', models.CharField(null=True, blank=True, max_length=200)),
                ('surname', models.CharField(null=True, blank=True, max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(null=True, blank=True, max_length=50)),
                ('organisation', models.CharField(null=True, blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ContactRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CramsToken',
            fields=[
                ('token_ptr', models.OneToOneField(serialize=False, auto_created=True, parent_link=True, to='authtoken.Token', primary_key=True)),
                ('ks_roles', models.TextField(null=True, blank=True)),
            ],
            bases=('authtoken.token',),
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('percentage', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='Duration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('duration', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=1)),
                ('duration_label', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FORCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('code', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='FundingBody',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='FundingScheme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('funding_scheme', models.CharField(max_length=200)),
                ('funding_body', models.ForeignKey(to='crams.FundingBody', related_name='funding_schemes')),
            ],
        ),
        migrations.CreateModel(
            name='Grant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('funding_body_and_scheme', models.CharField(max_length=200)),
                ('grant_id', models.CharField(blank=True, max_length=200)),
                ('start_year', models.IntegerField(validators=[django.core.validators.MinValueValidator(1970), django.core.validators.MaxValueValidator(3000)], error_messages={'min_value': 'Please input a year between 1970 ~ 3000', 'max_value': 'Please input a year between 1970 ~ 3000'}, default=2016)),
                ('total_funding', models.FloatField(blank=True, default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='GrantType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('notes', models.TextField(null=True, blank=True, max_length=1024)),
                ('created_by', models.ForeignKey(blank=True, related_name='project_created_by', null=True, to=settings.AUTH_USER_MODEL)),
                ('parent_project', models.ForeignKey(blank=True, null=True, to='crams.Project')),
                ('updated_by', models.ForeignKey(blank=True, related_name='project_updated_by', null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('contact', models.ForeignKey(to='crams.Contact', related_name='project_contacts')),
                ('contact_role', models.ForeignKey(to='crams.ContactRole', related_name='project_contacts')),
                ('project', models.ForeignKey(to='crams.Project', related_name='project_contacts')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectID',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('identifier', models.CharField(max_length=64)),
                ('project', models.ForeignKey(to='crams.Project', related_name='project_ids')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectIDSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('system', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectProvisionDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('project', models.ForeignKey(to='crams.Project', related_name='linked_provisiondetails')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectQuestionResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('question_response', models.TextField(blank=True, max_length=1024)),
                ('project', models.ForeignKey(to='crams.Project', related_name='project_question_responses')),
            ],
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('start_date', models.DateField(auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('crams_user', models.OneToOneField(blank=True, null=True, to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, related_name='provider_created_by', null=True, to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, related_name='provider_updated_by', null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProvisionDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('S', 'Sent'), ('P', 'Provisioned'), ('F', 'Failed'), ('X', 'Extend')], max_length=1, default='S')),
                ('message', models.TextField(null=True, blank=True)),
                ('created_by', models.ForeignKey(blank=True, related_name='provisiondetails_created_by', null=True, to=settings.AUTH_USER_MODEL)),
                ('provider', models.ForeignKey(to='crams.Provider', related_name='provisioned_requests')),
                ('updated_by', models.ForeignKey(blank=True, related_name='provisiondetails_updated_by', null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('reference', models.CharField(max_length=255)),
                ('project', models.ForeignKey(to='crams.Project', related_name='publications')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('key', models.CharField(max_length=50)),
                ('question_type', models.CharField(max_length=200)),
                ('question', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateField(default=datetime.date.today)),
                ('end_date', models.DateField()),
                ('approval_notes', models.TextField(null=True, blank=True, max_length=1024)),
                ('created_by', models.ForeignKey(blank=True, related_name='request_created_by', null=True, to=settings.AUTH_USER_MODEL)),
                ('funding_scheme', models.ForeignKey(to='crams.FundingScheme', related_name='requests')),
                ('parent_request', models.ForeignKey(blank=True, related_name='history', null=True, to='crams.Request')),
                ('project', models.ForeignKey(to='crams.Project', related_name='requests')),
            ],
        ),
        migrations.CreateModel(
            name='RequestQuestionResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('question_response', models.TextField(blank=True, max_length=1024)),
                ('question', models.ForeignKey(to='crams.Question', related_name='request_question_responses')),
                ('request', models.ForeignKey(to='crams.Request', related_name='request_question_responses')),
            ],
        ),
        migrations.CreateModel(
            name='RequestStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('code', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='StorageProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('funding_body', models.ForeignKey(to='crams.FundingBody', related_name='storageproduct')),
                ('provider', models.ForeignKey(to='crams.Provider', related_name='storageproduct')),
            ],
        ),
        migrations.CreateModel(
            name='StorageRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('quota', models.FloatField(default=0.0)),
                ('approved_quota', models.FloatField(default=0.0)),
                ('provision_details', models.OneToOneField(blank=True, related_name='storagerequest', null=True, to='crams.ProvisionDetails')),
                ('request', models.ForeignKey(to='crams.Request', related_name='storage_requests')),
                ('storage_product', models.ForeignKey(to='crams.StorageProduct', related_name='storage_requests')),
            ],
        ),
        migrations.CreateModel(
            name='StorageRequestQuestionResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('question_response', models.TextField(blank=True, max_length=1024)),
                ('question', models.ForeignKey(to='crams.Question', related_name='storage_question_responses')),
                ('storage_request', models.ForeignKey(to='crams.StorageRequest', related_name='storage_question_responses')),
            ],
        ),
        migrations.CreateModel(
            name='StorageType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('storage_type', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SupportedInstitution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('institution', models.CharField(max_length=200)),
                ('project', models.ForeignKey(to='crams.Project', related_name='institutions')),
            ],
        ),
        migrations.CreateModel(
            name='UserEvents',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('creation_ts', models.DateTimeField(auto_now_add=True)),
                ('last_modified_ts', models.DateTimeField(auto_now=True)),
                ('event_message', models.TextField()),
                ('created_by', models.ForeignKey(blank=True, related_name='userevents_created_by', null=True, to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, related_name='userevents_updated_by', null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='storageproduct',
            name='storage_type',
            field=models.ForeignKey(to='crams.StorageType', related_name='storage_products'),
        ),
        migrations.AddField(
            model_name='storageproduct',
            name='zone',
            field=models.ForeignKey(blank=True, related_name='storage_products', null=True, to='crams.Zone'),
        ),
        migrations.AddField(
            model_name='request',
            name='request_status',
            field=models.ForeignKey(to='crams.RequestStatus', related_name='requests'),
        ),
        migrations.AddField(
            model_name='request',
            name='updated_by',
            field=models.ForeignKey(blank=True, related_name='request_updated_by', null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='projectquestionresponse',
            name='question',
            field=models.ForeignKey(to='crams.Question', related_name='project_question_responses'),
        ),
        migrations.AddField(
            model_name='projectprovisiondetails',
            name='provision_details',
            field=models.ForeignKey(to='crams.ProvisionDetails', related_name='linked_projects'),
        ),
        migrations.AddField(
            model_name='projectid',
            name='system',
            field=models.ForeignKey(to='crams.ProjectIDSystem', related_name='project_ids'),
        ),
        migrations.AddField(
            model_name='grant',
            name='grant_type',
            field=models.ForeignKey(to='crams.GrantType', related_name='grants'),
        ),
        migrations.AddField(
            model_name='grant',
            name='project',
            field=models.ForeignKey(to='crams.Project', related_name='grants'),
        ),
        migrations.AddField(
            model_name='domain',
            name='for_code',
            field=models.ForeignKey(to='crams.FORCode', related_name='domains'),
        ),
        migrations.AddField(
            model_name='domain',
            name='project',
            field=models.ForeignKey(to='crams.Project', related_name='domains'),
        ),
        migrations.AddField(
            model_name='computerequestquestionresponse',
            name='question',
            field=models.ForeignKey(to='crams.Question', related_name='compute_question_responses'),
        ),
        migrations.AddField(
            model_name='computerequest',
            name='provision_details',
            field=models.OneToOneField(blank=True, related_name='computerequest', null=True, to='crams.ProvisionDetails'),
        ),
        migrations.AddField(
            model_name='computerequest',
            name='request',
            field=models.ForeignKey(to='crams.Request', related_name='compute_requests'),
        ),
        migrations.AddField(
            model_name='computeproduct',
            name='funding_body',
            field=models.ForeignKey(to='crams.FundingBody', related_name='computeproduct'),
        ),
        migrations.AddField(
            model_name='computeproduct',
            name='provider',
            field=models.ForeignKey(to='crams.Provider', related_name='computeproduct'),
        ),
    ]
