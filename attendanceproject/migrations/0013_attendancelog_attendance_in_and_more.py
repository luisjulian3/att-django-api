# Generated by Django 4.2.7 on 2024-02-22 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendanceproject', '0012_alter_officemaster_office_lat_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendancelog',
            name='attendance_in',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='attendancelog',
            name='attendance_out',
            field=models.BooleanField(default=False),
        ),
    ]
