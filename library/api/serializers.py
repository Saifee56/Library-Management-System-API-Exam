from . models import BookModel
from rest_framework import serializers
from django.contrib.auth.models import User

# Book Serializer
class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model=BookModel
        fields='__all__'


# Admin LogIn Serializer
class AdminLoginSerializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField()

# User Login Serializer
class UserRegisterSerializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField()
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user