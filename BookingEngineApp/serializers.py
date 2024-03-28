from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from BookingEngineApp.models import UserRegistration, Facility, Room, RoomCategory, Package, Booking, Contact


# User Register 

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegistration
        # declearing fields to serialize 
        fields = ['username', 'email' , 'first_name', 'last_name', 'password','profile_picture']

    # encrypting the password
    def save(self, **kwargs):
        self.validated_data['password'] = make_password(self.validated_data['password'])
        super().save(**kwargs)


# Update Profile Picture

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegistration
        fields = ['username', 'email' , 'first_name', 'last_name','profile_picture','total_bookings_rewards']
        read_only_fields = ['total_bookings_rewards']
    

# Verify Account

class VerifyAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()


# User Login

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


# Admin Panel

class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = "__all__"

class RoomCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomCategory
        fields = "__all__"

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['number', 'price', 'name', 'type', 'image', 'facility', 'sleeps','credits_received', 'credits_required']
        read_only_fields = ['credits_received', 'credits_required']


# Reset Password

class ResetPasswordSerializer(serializers.Serializer):
    oldpassword = serializers.CharField(required = True)
    newpassword = serializers.CharField(required = True)


# Package

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = "__all__"


# Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


# Book Rooms

class BookingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Booking
        fields = ['name','check_in','check_out', 'adult', 'children', 'occupancy', 'total_price', 'grand_total', 'booking_rewards', 'booking_credits','stay_duration']
        read_only_fields = ['occupancy', 'total_price', 'grand_total', 'booking_rewards', 'booking_credits','stay_duration']

