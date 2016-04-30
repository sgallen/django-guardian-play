from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    is_managed = models.BooleanField(default=True)

    class Meta:
        permissions = (
            ('view_organization', 'Can view organization'),
        )
        get_latest_by = 'created_at'

    def __unicode__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=128)
    organization = models.ForeignKey(Organization)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        permissions = (
            ('view_company', 'Can view company'),
        )
        get_latest_by = 'created_at'

    def __unicode__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=128)
    company = models.ForeignKey(Company)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        permissions = (
            ('view_project', 'Can view project'),
        )
        get_latest_by = 'created_at'

    def __unicode__(self):
        return self.name
