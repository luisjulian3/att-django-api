# Generated by Django 4.2.7 on 2023-11-23 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendanceproject', '0002_attendancelog_faceimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='bind',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.IntegerField(default=0),
        ),
    ]
