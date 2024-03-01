from django.db import models


class User(models.Model):
    nik = models.CharField(primary_key=True, max_length=18, unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(
        max_length=255)
    create_at = models.DateTimeField(auto_now_add=True)
    bind = models.BooleanField(default=False)
    status = models.IntegerField(default=0)
    role_id = models.IntegerField(choices=[
        (0, 'Admin'),
        (1, 'Employee'),
        (2, 'Coordinator'),
        (3, 'Junior Manager'),
        (4, 'Senior Manager'),
        (5, 'General Manager'),
    ])
    dept_id = models.IntegerField(choices=[
        (0, 'Admin'),
        (1, 'IT & Tech Product'),
        (2, 'Commercial'),
        (3, 'Finance & Human Capital'),
        (4, 'Operation'),
        (5, 'Sales'),
    ])


class AttendanceLog(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_logs')
    nik = models.IntegerField()
    presence_status = models.CharField(max_length=10)
    attendance_in_status = models.CharField(max_length=10)
    attendance_office = models.CharField(max_length=10)
    attendance_date = models.DateField()
    attendance_in_time = models.TimeField()
    attendance_out_time = models.TimeField(null=True, blank=True)
    working_hours = models.DurationField(null=True, blank=True)
    longitude_in = models.DecimalField(max_digits=9, decimal_places=6)
    latitude_in = models.DecimalField(max_digits=9, decimal_places=6)
    longitude_out = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    latitude_out = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)


class FaceImage(models.Model):
    id = models.AutoField(primary_key=True)
    nik = models.IntegerField(default=0)
    image_id = models.CharField(max_length=255)
    image = models.ImageField(upload_to='face_images/', null=True, blank=True)
    full_name = models.CharField(max_length=255)
    image_path = models.CharField(max_length=255)


class OfficeMaster(models.Model):
    office_id = models.AutoField(primary_key=True)
    office_name = models.CharField(max_length=100)
    office_lat = models.DecimalField(max_digits=17, decimal_places=15)
    office_long = models.DecimalField(max_digits=18, decimal_places=15)


class RoleMaster(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=100)
    attendance_employee_log = models.BooleanField(default=False)
    register_employee = models.BooleanField(default=False)
    settings_employee = models.BooleanField(default=False)


class PresenceStatusMaster(models.Model):
    presence_id = models.AutoField(primary_key=True)
    presence_code = models.CharField(max_length=10, unique=True)
    presence_name = models.CharField(max_length=100)
