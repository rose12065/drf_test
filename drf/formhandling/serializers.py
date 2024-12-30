# serializers.py
from rest_framework import serializers
from .models import CustomUser, Item

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'date_of_birth', 'profile_picture', 'role', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['category', 'subcategory', 'name', 'amount'] # feilds or exclude is a mandatory feild 

        
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
