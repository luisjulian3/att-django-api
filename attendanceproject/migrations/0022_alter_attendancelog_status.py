# Generated by Django 4.2.7 on 2024-02-26 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendanceproject', '0021_alter_attendancelog_presence_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendancelog',
            name='status',
            field=models.CharField(max_length=5),
        ),
    ]
