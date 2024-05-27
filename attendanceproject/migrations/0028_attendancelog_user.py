# Generated by Django 4.2.7 on 2024-02-27 19:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendanceproject', '0027_user_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendancelog',
            name='user',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='attendance_logs', to='attendanceproject.user'),
            preserve_default=False,
        ),
    ]