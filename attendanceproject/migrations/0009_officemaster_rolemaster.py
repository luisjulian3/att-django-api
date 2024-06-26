# Generated by Django 4.2.7 on 2024-02-09 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendanceproject', '0008_faceimage_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfficeMaster',
            fields=[
                ('office_id', models.AutoField(primary_key=True, serialize=False)),
                ('office_name', models.CharField(max_length=100)),
                ('office_lat', models.DecimalField(decimal_places=8, max_digits=12)),
                ('office_long', models.DecimalField(decimal_places=8, max_digits=13)),
            ],
        ),
        migrations.CreateModel(
            name='RoleMaster',
            fields=[
                ('role_id', models.AutoField(primary_key=True, serialize=False)),
                ('role_name', models.CharField(max_length=100)),
                ('admin_menu', models.BooleanField(default=False)),
                ('attendance_employee_log', models.BooleanField(default=False)),
                ('register_member', models.BooleanField(default=False)),
            ],
        ),
    ]
