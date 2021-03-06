# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Airports(models.Model):
    id = models.IntegerField(primary_key=True)
    icao_code = models.CharField(max_length=7, blank=True, null=True)
    type = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=80, blank=True, null=True)
    latitude_deg = models.FloatField(blank=True, null=True)
    longitude_deg = models.FloatField(blank=True, null=True)
    elevation_ft = models.CharField(max_length=7, blank=True, null=True)
    continent = models.CharField(max_length=2, blank=True, null=True)
    iso_country = models.CharField(max_length=2, blank=True, null=True)
    iso_region = models.CharField(max_length=7, blank=True, null=True)
    municipality = models.CharField(max_length=80, blank=True, null=True)
    scheduled_service = models.CharField(max_length=5, blank=True, null=True)
    gps_code = models.CharField(max_length=7, blank=True, null=True)
    iata_code = models.CharField(max_length=3, blank=True, null=True)
    local_code = models.CharField(max_length=10, blank=True, null=True)
    home_link = models.CharField(max_length=200, blank=True, null=True)
    wikipedia_link = models.CharField(max_length=200, blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    url_name = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'airports'


class AirportsArrDep(models.Model):
    icao = models.CharField(max_length=10)
    arrival_func = models.CharField(max_length=150, blank=True, null=True)
    departures_func = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'airports_arr_dep'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Country(models.Model):
    iso = models.CharField(max_length=2)
    name = models.CharField(max_length=80)
    nicename = models.CharField(max_length=80)
    iso3 = models.CharField(max_length=3, blank=True, null=True)
    numcode = models.SmallIntegerField(blank=True, null=True)
    phonecode = models.IntegerField()
    urlname = models.CharField(max_length=80, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'country'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class FlightData(models.Model):
    acid = models.CharField(primary_key=True, max_length=32)
    airline = models.CharField(max_length=32, blank=True, null=True)
    arrival_arpt = models.CharField(max_length=32)
    departure_arpt = models.CharField(max_length=32)
    est_dep_time = models.DateTimeField()
    status = models.CharField(max_length=150, blank=True, null=True)
    scheduled_arr_time = models.DateTimeField(blank=True, null=True)
    aircraft = models.CharField(max_length=10, blank=True, null=True)
    gufi = models.CharField(max_length=15, blank=True, null=True)
    act_dep_time = models.DateTimeField(blank=True, null=True)
    est_arr_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'flight_data'
        unique_together = (('acid', 'est_dep_time'),)
