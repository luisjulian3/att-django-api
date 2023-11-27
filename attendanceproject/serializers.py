from django.contrib.auth.hashers import check_password, make_password
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

User = User


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('nik', 'full_name', 'date_of_birth', 'place_of_birth', 'email', 'password', 'role_id', 'dept_id')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        nik = attrs.get('nik')

        # Check if a user with the same 'nik' exists in the database
        if User.objects.filter(nik=nik).exists():
            raise serializers.ValidationError("User with this nik already exists.")

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


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('nik', 'password')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nik', 'password','email']
