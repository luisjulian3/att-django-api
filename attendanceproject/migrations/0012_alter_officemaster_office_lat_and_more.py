# Generated by Django 4.2.7 on 2024-02-22 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendanceproject', '0011_rename_register_member_rolemaster_register_employee_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='officemaster',
            name='office_lat',
            field=models.DecimalField(decimal_places=15, max_digits=17),
        ),
        migrations.AlterField(
            model_name='officemaster',
            name='office_long',
            field=models.DecimalField(decimal_places=15, max_digits=18),
        ),
        migrations.AlterField(
            model_name='user',
            name='nik',
            field=models.CharField(max_length=18, unique=True),
        ),
    ]