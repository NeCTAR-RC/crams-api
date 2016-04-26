# coding=utf-8
"""
Admin File
"""
# Register your models here.
from django.contrib import admin
from crams.models import Request, Project, ProjectContact, Contact, FundingBody, \
    FundingScheme, ProjectID, ContactRole, Question, RequestStatus, Provider, \
    StorageProduct, ComputeProduct, StorageRequest, ProvisionDetails, \
    ComputeRequest, Zone, ProjectIDSystem, CramsToken

__author__ = 'rafi m feroze'  # 'mmohamed'

# from account.models import User
# admin.site.register(User)


class RequestAdmin(admin.ModelAdmin):
    """
    class RequestAdmin
    """
    list_display = ('id', 'project', 'funding_scheme', 'start_date',
                    'end_date', 'request_status', 'parent_request')
admin.site.register(Request, RequestAdmin)


class ProjectAdmin(admin.ModelAdmin):
    """
    class ProjectAdmin
    """
    list_display = ('id', 'title', 'description', 'parent_project')
admin.site.register(Project, ProjectAdmin)


class ContactAdmin(admin.ModelAdmin):
    """
    class ContactAdmin
    """
    list_display = ('given_name', 'surname', 'email')
admin.site.register(Contact, ContactAdmin)


class ProjectContactAdmin(admin.ModelAdmin):
    """
    class ProjectContactAdmin
    """
    list_display = ('project', 'contact', 'contact_role')
admin.site.register(ProjectContact, ProjectContactAdmin)
admin.site.register(ContactRole)


class FundingSchemeAdmin(admin.ModelAdmin):
    """
    class FundingSchemeAdmin
    """
    list_display = ('id', 'funding_scheme', 'funding_body')
admin.site.register(FundingScheme, FundingSchemeAdmin)


class FundingBodyAdmin(admin.ModelAdmin):
    """
    class FundingBodyAdmin
    """
    list_display = ('id', 'name')
admin.site.register(FundingBody, FundingBodyAdmin)

admin.site.register(Provider)


class CramsTokenAdmin(admin.ModelAdmin):
    """
    class FundingBodyAdmin
    """
    list_display = ('user', 'key', 'ks_roles')
admin.site.register(CramsToken, CramsTokenAdmin)
admin.site.register(ComputeProduct)
admin.site.register(ProjectID)
admin.site.register(ProjectIDSystem)
admin.site.register(Question)
admin.site.register(RequestStatus)
admin.site.register(Zone)


class ComputeRequestInline(admin.TabularInline):
    """
    class ComputeRequestInline
    """
    model = ComputeRequest


class StorageRequestInline(admin.TabularInline):
    """
    class StorageRequestInline
    """
    model = StorageRequest


class ProvisionDetailsAdmin(admin.ModelAdmin):
    """
    class ProvisionDetailsAdmin
    """
    list_display = ('id', 'status', 'provider', 'last_modified_ts')
    inlines = [
        ComputeRequestInline,
        StorageRequestInline
    ]
admin.site.register(ProvisionDetails, ProvisionDetailsAdmin)


class StorageProductAdmin(admin.ModelAdmin):
    """
    class StorageProductAdmin
    """
    list_display = ('id', 'name', 'zone', 'provider', 'storage_type')
admin.site.register(StorageProduct, StorageProductAdmin)


class StorageRequestAdmin(admin.ModelAdmin):
    """
    class StorageRequestAdmin
    """
    list_display = ('id', 'approved_quota', 'request',
                    'storage_product', 'provision_details', 'request')
admin.site.register(StorageRequest, StorageRequestAdmin)


class ComputeRequestAdmin(admin.ModelAdmin):
    """
    class ComputeRequestAdmin
    """
    list_display = (
        'id',
        'instances',
        'cores',
        'core_hours',
        'provision_details',
        'approved_instances',
        'approved_cores',
        'approved_core_hours',
        'request')
admin.site.register(ComputeRequest, ComputeRequestAdmin)
