from django.contrib.auth.models import Group, User
from django.test import TestCase

from .models import (
    Organization,
    Company,
    Project,
    Task,
    ORGANIZATION_ROLE_NAMES,
    COMPANY_ROLE_NAMES,
)


class UserPermissionTest(TestCase):
    def setUp(self):
        self.moose_usa = Organization.objects.create(name='Moose USA', is_managed=False)
        self.moose_usa_att = Company.objects.create(name='AT&T', organization=self.moose_usa)
        self.moose_usa_honda = Company.objects.create(name='Honda USA', organization=self.moose_usa)
        self.moose_usa_honda_ny = Project.objects.create(name='NY Honda', company=self.moose_usa_honda)

        self.moose_can = Organization.objects.create(name='Moose CAN')
        self.moose_can_honda = Company.objects.create(name='Honda CAN', organization=self.moose_can)
        self.moose_can_honda_bc = Project.objects.create(name='BC Honda', company=self.moose_can_honda)

        # Groups (created as part of the Organization and Company creation)
        admin_group = Group.objects.get(name='Admin')
        manager_group = Group.objects.get(name='Manager')
        moose_can_admin_group = Group.objects.get(name=ORGANIZATION_ROLE_NAMES['admin'].format('Moose CAN'))
        moose_can_observer_group = Group.objects.get(name=ORGANIZATION_ROLE_NAMES['observer'].format('Moose CAN'))
        honda_usa_admin_group = Group.objects.get(name=COMPANY_ROLE_NAMES['admin'].format('Honda USA'))
        honda_usa_observer_group = Group.objects.get(name=COMPANY_ROLE_NAMES['observer'].format('Honda USA'))

        # Admin user
        self.global_admin_user = User.objects.create(username='Anne')
        self.global_admin_user.groups.add(admin_group)

        # Managed service user
        self.manager_user = User.objects.create(username='Mary')
        self.manager_user.groups.add(manager_group)

        # Users at the organization level
        self.moose_can_admin = User.objects.create(username='moose_can_admin')
        self.moose_can_admin.groups.add(moose_can_admin_group)
        self.moose_can_observer = User.objects.create(username='moose_can_observer')
        self.moose_can_observer.groups.add(moose_can_observer_group)

        # Users at the company level
        self.moose_usa_honda_admin = User.objects.create(username='moose_usa_honda_admin')
        self.moose_usa_honda_admin.groups.add(honda_usa_admin_group)
        self.moose_usa_honda_observer = User.objects.create(username='moose_usa_honda_observer')
        self.moose_usa_honda_observer.groups.add(honda_usa_observer_group)

    # Admin role
    def test_admin_has_project_change_access(self):
        self.assertTrue(self.moose_can_admin.has_perm('change_project', self.moose_can_honda_bc))

    # Manager role
    def test_manager_has_project_change_access(self):
        self.assertTrue(self.manager_user.has_perm('change_project', self.moose_can_honda_bc))

    def test_manager_has_no_project_change_access_for_unmanaged_organization(self):
        self.assertFalse(self.manager_user.has_perm('change_project', self.moose_usa_honda_ny))

    # Organization roles
    def test_org_admin_user_can_change_child_project(self):
        self.assertTrue(self.moose_can_admin.has_perm('change_project', self.moose_can_honda_bc))

    def test_org_observer_user_cant_change_child_project(self):
        self.assertFalse(self.moose_can_observer.has_perm('change_project', self.moose_can_honda_bc))

    def test_org_observer_user_can_view_child_project(self):
        self.assertTrue(self.moose_can_observer.has_perm('view_project', self.moose_can_honda_bc))

    def test_org_admin_user_cant_change_unrelated_child_project(self):
        self.assertFalse(self.moose_can_admin.has_perm('change_project', self.moose_usa_honda_ny))

    # Company roles
    def test_company_admin_user_can_change_child_project(self):
        self.assertTrue(self.moose_usa_honda_admin.has_perm('change_project', self.moose_usa_honda_ny))

    def test_company_admin_user_cant_change_parent_organization(self):
        self.assertFalse(self.moose_usa_honda_admin.has_perm('change_organization', self.moose_usa))

    def test_company_observer_user_cant_change_child_project(self):
        self.assertFalse(self.moose_usa_honda_observer.has_perm('change_project', self.moose_usa_honda_ny))

    def test_company_observer_user_can_view_child_project(self):
        self.assertTrue(self.moose_usa_honda_observer.has_perm('view_project', self.moose_usa_honda_ny))

    def test_company_admin_user_cant_change_unrelated_child_project(self):
        self.assertFalse(self.moose_usa_honda_admin.has_perm('change_project', self.moose_can_honda_bc))
