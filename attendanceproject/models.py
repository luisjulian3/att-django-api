from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    nik = models.IntegerField(default=0)
    full_name = models.CharField(max_length=255)
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
    nik = models.IntegerField()
    status = models.IntegerField(choices=[(0, 'Failed'), (1, 'Success')])
    attendance_date = models.DateField()
    attendance_in_time = models.DateTimeField()
    attendance_in_date = models.DateField()
    attendance_out_time = models.DateTimeField()
    attendance_out_date = models.DateField()
    working_hours = models.DurationField()
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)


class FaceImage(models.Model):
    id = models.AutoField(primary_key=True)
    nik = models.IntegerField(default=0)
    image_id = models.CharField(max_length=255)
    image = models.ImageField(upload_to='face_images/', null=True, blank=True)
    full_name = models.CharField(max_length=255)
    image_path = models.CharField(max_length=255)
