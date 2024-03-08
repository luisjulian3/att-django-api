from datetime import datetime

from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Avg
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, AttendanceLog

User = User


class RegistrationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='nik', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'nik', 'full_name', 'date_of_birth', 'place_of_birth', 'email', 'password', 'role_id', 'dept_id',
            'phone')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        nik = attrs.get('nik')

        # Check if a user with the same 'nik' exists in the database
        if User.objects.filter(nik=nik).exists():
            raise serializers.ValidationError({"status": "User with this nik already exists."})

        return attrs

    def create(self, validated_data):
        # Extract and remove 'password' from validated data
        password = validated_data.pop('password', None)

        # Hash the password
        if password:
            validated_data['password'] = make_password(password)

        # Create a new user instance with the updated validated data
        user = User.objects.create(**validated_data)
        return user

    def to_representation(self, instance):
        """
        Serialize instance to representation.
        """
        representation = super().to_representation(instance)
        representation['id'] = representation['nik']  # Set 'id' field value equal to 'nik' value
        return representation


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('nik', 'password')


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['nik', 'email', 'full_name', 'phone', 'date_of_birth', 'place_of_birth', 'bind', 'status', 'role_id',
                  'dept_id', 'role', 'department']

    def get_role(self, obj):
        return dict(obj._meta.get_field('role_id').choices).get(obj.role_id, '')

    def get_department(self, obj):
        return dict(obj._meta.get_field('dept_id').choices).get(obj.dept_id, '')


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'nik']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'email', 'bind', 'role_id', 'dept_id']


class AttendanceLogSerializer(serializers.ModelSerializer):
    day = serializers.SerializerMethodField()

    def get_day(self, obj):
        # Ambil tanggal dari attendance_date
        date = obj.attendance_date

        # Ubah ke format tanggal untuk mendapatkan hari
        day = datetime.strftime(date, '%A')  # %A akan memberikan nama hari lengkap (e.g., Monday)

        return day

    class Meta:
        model = AttendanceLog
        fields = ['nik', 'attendance_date', 'attendance_in_time', 'attendance_out_time',
                  'working_hours', 'presence_status', 'latitude_in', 'longitude_in',
                  'latitude_out', 'longitude_out', 'attendance_in_status', 'attendance_office', 'day']


class UserDashboardAttendanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLog
        fields = ['attendance_date', 'attendance_in_time', 'attendance_out_time', 'presence_status']


class UserDashboardSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    average_attendance_in_time = serializers.SerializerMethodField()
    average_attendance_out_time = serializers.SerializerMethodField()
    average_working_hours = serializers.SerializerMethodField()

    def get_role(self, obj):
        return dict(obj._meta.get_field('role_id').choices).get(obj.role_id, '')

    def get_department(self, obj):
        return dict(obj._meta.get_field('dept_id').choices).get(obj.dept_id, '')

    def get_average_attendance_in_time(self, obj):
        queryset = AttendanceLog.objects.all()
        average_duration = queryset.aggregate(avg_attendance_in_time=Avg('attendance_in_time'))
        return self.format_duration(average_duration['avg_attendance_in_time'])

    def get_average_attendance_out_time(self, obj):
        queryset = AttendanceLog.objects.all()
        average_duration = queryset.aggregate(avg_attendance_out_time=Avg('attendance_out_time'))
        return self.format_duration(average_duration['avg_attendance_out_time'])

    def get_average_working_hours(self, obj):
        queryset = AttendanceLog.objects.all()
        average_duration = queryset.aggregate(avg_working_hours=Avg('working_hours'))
        return self.format_duration(average_duration['avg_working_hours'])

    def format_duration(self, duration):
        if duration is not None:
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
        else:
            return '00:00:00'

    class Meta:
        model = User
        fields = ['nik', 'full_name', 'role', 'department', 'email', 'phone', 'average_attendance_in_time',
                  'average_attendance_out_time', 'average_working_hours']
