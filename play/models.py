from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models

from guardian.shortcuts import assign_perm


ORGANIZATION_ROLE_NAMES = {
    'admin': 'Organization:{}:Admin',
    'observer': 'Organization:{}:Observer',
}

COMPANY_ROLE_NAMES = {
    'admin': 'Company:{}:Admin',
    'observer': 'Company:{}:Observer',
}

class RolesMixin():
    def get_organization(self):
        raise NotImplementedError

    def get_company(self):
        raise NotImplementedError

    def roles_init_new(self):
        '''Get or create groups and assign object.
            Roles:
            - Admin: all permissions on object
            - Observer: only view permission on object
        '''
        organization = self.get_organization()
        company = self.get_company()
        g_admin, _ = Group.objects.get_or_create(name='Admin')
        g_manager, _ = Group.objects.get_or_create(name='Manager')
        g_organization_admin, _ = Group.objects.get_or_create(name=ORGANIZATION_ROLE_NAMES['admin'].format(organization.name))
        g_organization_observer, _ = Group.objects.get_or_create(name=ORGANIZATION_ROLE_NAMES['observer'].format(organization.name))
        g_company_admin, _ = Group.objects.get_or_create(name=COMPANY_ROLE_NAMES['admin'].format(company.name))
        g_company_observer, _ = Group.objects.get_or_create(name=COMPANY_ROLE_NAMES['observer'].format(company.name))

        model_name = self.__class__.__name__.lower()
        model_content_type = ContentType.objects.get(model=model_name)
        # full_permissions = ('add_company', 'change_company', 'delete_company', 'view_company',)
        full_permissions = (permission.codename for permission in Permission.objects.filter(content_type=model_content_type))
        view_permissions = ('view_{}'.format(model_name),)

        for permission in full_permissions:
            assign_perm(permission, g_admin, self)
            if organization.is_managed:
                assign_perm(permission, g_manager, self)
            assign_perm(permission, g_organization_admin, self)
            assign_perm(permission, g_company_admin, self)

        for permission in view_permissions:
            assign_perm(permission, g_organization_observer, self)
            assign_perm(permission, g_company_observer, self)


class Organization(models.Model):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    is_managed = models.BooleanField(default=True)

    class Meta:
        permissions = (
            ('view_organization', 'Can view organization'),
        )
        get_latest_by = 'created_at'

    def __str__(self):
        return self.name

    def roles_init_new(self):
        '''Get or create groups and assign object.
            Roles:
            - Admin: all permissions on object
            - Observer: only view permission on object
        '''
        g_admin, _ = Group.objects.get_or_create(name='Admin')
        g_manager, _ = Group.objects.get_or_create(name='Manager')
        g_organization_admin, _ = Group.objects.get_or_create(name=ORGANIZATION_ROLE_NAMES['admin'].format(self.name))
        g_organization_observer, _ = Group.objects.get_or_create(name=ORGANIZATION_ROLE_NAMES['observer'].format(self.name))

        full_permissions = ('add_organization', 'change_organization', 'delete_organization', 'view_organization',)
        view_permissions = ('view_organization',)

        # Assign full permissions to Admin and Organization Admin.
        # Assign full permissions to Managers only if organization is managed.
        for permission in full_permissions:
            assign_perm(permission, g_admin, self)
            assign_perm(permission, g_organization_admin, self)
            if self.is_managed:
                assign_perm(permission, g_manager, self)

        assign_perm('view_organization', g_organization_observer, self)

    def save(self, *args, **kwargs):
        is_create = False
        if not self.id:
            is_create = True

        super().save(*args, **kwargs)
        if is_create:
            self.roles_init_new()


class Company(RolesMixin, models.Model):
    name = models.CharField(max_length=128)
    organization = models.ForeignKey(Organization)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        permissions = (
            ('view_company', 'Can view company'),
        )
        get_latest_by = 'created_at'

    def __str__(self):
        return self.name

    def get_organization(self):
        return self.organization

    def get_company(self):
        return self

    def save(self, *args, **kwargs):
        is_create = False
        if not self.id:
            is_create = True

        super().save(*args, **kwargs)
        if is_create:
            self.roles_init_new()


class Project(RolesMixin, models.Model):
    name = models.CharField(max_length=128)
    company = models.ForeignKey(Company)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        permissions = (
            ('view_project', 'Can view project'),
        )
        get_latest_by = 'created_at'

    def __str__(self):
        return self.name

    def get_organization(self):
        return self.company.organization

    def get_company(self):
        return self.company

    def save(self, *args, **kwargs):
        is_create = False
        if not self.id:
            is_create = True

        super().save(*args, **kwargs)
        if is_create:
            self.roles_init_new()


class Task(RolesMixin, models.Model):
    name = models.CharField(max_length=128)
    project = models.ForeignKey(Project)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        permissions = (
            ('view_task', 'Can view task'),
        )
        get_latest_by = 'created_at'

    def __str__(self):
        return self.name

    def get_organization(self):
        return self.project.company.organization

    def get_company(self):
        return self.project.company

    def save(self, *args, **kwargs):
        is_create = False
        if not self.id:
            is_create = True

        super().save(*args, **kwargs)
        if is_create:
            self.roles_init_new()

# TODO: If we had a Group* class for each subordinate class e.g. GroupProject,
# when calling roles_init_new could inspect the groups to which the immediate
# parent belongs and assign the obj to that group.
