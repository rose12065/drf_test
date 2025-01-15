# serializers.py
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from django.core.mail import send_mail
from django.utils.timezone import now

from .services import UserValidationService
from .models import CustomUser, Item, LoginAttempt


# model serializer for registration
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'date_of_birth', 'profile_picture', 'role', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            date_of_birth=validated_data['date_of_birth'],
            profile_picture=validated_data['profile_picture'],
            role=validated_data['role'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# Model serializer for items
class ItemSerializer(serializers.Serializer):
    category= serializers.CharField()
    subcategory=serializers.CharField()
    name=serializers.CharField()
    amount=serializers.IntegerField()
    
    def create(self, validated_data):
        return Item.objects.create(**validated_data)
    
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Use the validation service
        try:
            user = UserValidationService(email, password)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

        data['user'] = user
        return data
    