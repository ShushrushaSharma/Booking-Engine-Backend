from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from BookingEngineApp.models import UserRegistration, Facility, Room, RoomImage


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegistration
        # declearing fields to serialize 
        fields = ['username', 'email' , 'first_name', 'last_name', 'password']

    # encrypting the password
    def save(self, **kwargs):
        self.validated_data['password'] = make_password(self.validated_data['password'])
        super().save(**kwargs)


# User Login
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


# Admin Panel

class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = "__all__"

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"

class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = "__all__"


# Reset Password

class ResetPasswordSerializer(serializers.Serializer):
    oldpassword = serializers.CharField(required = True)
    newpassword = serializers.CharField(required = True)