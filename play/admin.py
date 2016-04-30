from django.contrib import admin

from guardian.admin import GuardedModelAdmin

from .models import (
    Organization,
    Company,
    Project,
    Task,
)


class OrganizationAdmin(GuardedModelAdmin):
    list_display = ('name', 'created_at')
    ordering = ('-created_at',)

class CompanyAdmin(GuardedModelAdmin):
    list_display = ('name', 'get_organization', 'created_at')
    ordering = ('-created_at',)

class ProjectAdmin(GuardedModelAdmin):
    list_display = ('name', 'get_organization', 'get_company', 'created_at')
    ordering = ('-created_at',)

class TaskAdmin(GuardedModelAdmin):
    list_display = ('name', 'get_organization', 'get_company', 'project', 'created_at')
    ordering = ('-created_at',)

admin.site.register(Company, CompanyAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
