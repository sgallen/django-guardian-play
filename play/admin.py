from django.contrib import admin

from guardian.admin import GuardedModelAdmin

from .models import (
    Company,
    Organization,
    Project,
)


class CompanyAdmin(GuardedModelAdmin):
    ordering = ('-created_at',)

class OrganizationAdmin(GuardedModelAdmin):
    ordering = ('-created_at',)

class ProjectAdmin(GuardedModelAdmin):
    ordering = ('-created_at',)

admin.site.register(Company, CompanyAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Project, ProjectAdmin)
