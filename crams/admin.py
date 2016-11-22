# coding=utf-8
"""
Admin File
"""

from django.contrib import admin
from crams import models


class RequestAdmin(admin.ModelAdmin):
    """
    class RequestAdmin
    """
    list_display = ('id', 'project', 'funding_scheme', 'start_date',
                    'end_date', 'request_status', 'parent_request')


class ProjectAdmin(admin.ModelAdmin):
    """
    class ProjectAdmin
    """
    list_display = ('id', 'title', 'description', 'parent_project')


class ContactAdmin(admin.ModelAdmin):
    """
    class ContactAdmin
    """
    list_display = ('given_name', 'surname', 'email')


class ProjectContactAdmin(admin.ModelAdmin):
    """
    class ProjectContactAdmin
    """
    list_display = ('project', 'contact', 'contact_role')


class FundingSchemeAdmin(admin.ModelAdmin):
    """
    class FundingSchemeAdmin
    """
    list_display = ('id', 'funding_scheme', 'funding_body')


class FundingBodyAdmin(admin.ModelAdmin):
    """
    class FundingBodyAdmin
    """
    list_display = ('id', 'name')


class CramsTokenAdmin(admin.ModelAdmin):
    """
    class FundingBodyAdmin
    """
    list_display = ('user', 'key', 'ks_roles')


class ComputeRequestInline(admin.TabularInline):
    """
    class ComputeRequestInline
    """
    model = models.ComputeRequest


class StorageRequestInline(admin.TabularInline):
    """
    class StorageRequestInline
    """
    model = models.StorageRequest


class ProvisionDetailsAdmin(admin.ModelAdmin):
    """
    class ProvisionDetailsAdmin
    """
    list_display = ('id', 'status', 'provider', 'last_modified_ts')
    inlines = [
        ComputeRequestInline,
        StorageRequestInline
    ]


class StorageProductAdmin(admin.ModelAdmin):
    """
    class StorageProductAdmin
    """
    list_display = ('id', 'name', 'zone', 'provider', 'storage_type')


class StorageRequestAdmin(admin.ModelAdmin):
    """
    class StorageRequestAdmin
    """
    list_display = ('id', 'approved_quota', 'request',
                    'storage_product', 'provision_details', 'request')


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


admin.site.register(models.Request, RequestAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Contact, ContactAdmin)
admin.site.register(models.ProjectContact, ProjectContactAdmin)
admin.site.register(models.ContactRole)
admin.site.register(models.FundingScheme, FundingSchemeAdmin)
admin.site.register(models.FundingBody, FundingBodyAdmin)
admin.site.register(models.Provider)
admin.site.register(models.CramsToken, CramsTokenAdmin)
admin.site.register(models.ComputeProduct)
admin.site.register(models.ProjectID)
admin.site.register(models.ProjectIDSystem)
admin.site.register(models.Question)
admin.site.register(models.RequestStatus)
admin.site.register(models.Zone)
admin.site.register(models.ProvisionDetails, ProvisionDetailsAdmin)
admin.site.register(models.StorageProduct, StorageProductAdmin)
admin.site.register(models.StorageRequest, StorageRequestAdmin)
admin.site.register(models.ComputeRequest, ComputeRequestAdmin)
