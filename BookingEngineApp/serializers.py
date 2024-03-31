from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from BookingEngineApp.models import UserRegistration, Facility, Room, RoomCategory, Package, Booking, Contact

from django.conf import settings
import json
import requests
from rest_framework import exceptions


# User Register 

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegistration
        # declearing fields to serialize 
        fields = ['username', 'email' , 'first_name', 'last_name', 'password','profile_picture', 'total_bookings_rewards']
        read_only_fields = ['total_bookings_rewards']

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

    def validate(self, data):
        name = data.get('name')
        occupancy = data.get('occupancy')
        
        if name and occupancy is not None:
            room = Room.objects.get(name=name)
            if occupancy > room.sleep:
                raise serializers.ValidationError("Occupancy cannot be more than room limit")
        
        return data
    

# Khalti Payments

class KhaltiSerializer(serializers.Serializer):
    purchase_order_id = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=9, decimal_places=2)
    purchase_order_name = serializers.CharField()

    def create(self, validated_data):
        
        secret_key = settings.KHATI_SECRET_KEY
        initiate_url = settings.KHALTI_INITIATE_URL

        headers = {
            "Authorization": f"key {secret_key}",
            "Content-Type": "application/json",
        }

        purchase_order_id = validated_data.get("purchase_order_id")
        amount = validated_data.get("amount")

        payload = {
            "purchase_order_id": purchase_order_id,
            "amount": str(amount),  
            "purchase_order_name": validated_data.get("purchase_order_name"),
            "return_url": "http://localhost:3000/",
            "website_url": "http://127.0.0.1:8000/"
        }

        try:
            payload = json.dumps(payload)
            response = requests.request("POST", initiate_url, headers=headers, data=payload)
            data = json.loads(response.text)
            data = json.loads(response.text)
            error_detail = data.get("detail")

            if error_detail:
                raise exceptions.ValidationError({"khalti_error": [error_detail]})

            # including pidx in the returned data

            payment_id = data.get("pidx")
            data["pidx"] = payment_id

            return data
        
        except (requests.RequestException, ValueError) as e:
            raise exceptions.APIException("Failed to initiate payment. Please try again later.")


class KhaltiSerializerAfterInitiate(serializers.Serializer):

    def create(self, validated_data):

        secret_key = settings.KHATI_SECRET_KEY
        request = self.context.get("request")
        token = request.query_params.get("pidx")
        lookup_url = settings.KHALTI_LOOK_URL

        payload = {
            "pidx": token,
        }
        headers = {"Authorization": f"key {secret_key}"}

        try:
            response = requests.request("POST", lookup_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  
            response_data_json = response.json()
            status = response_data_json.get("status")
            
            if status and status.lower() == "completed":
                success_message = "Thank you for your payment! Your transaction was successful."
                return {"success": True, "message": success_message, "payment_id": response_data_json.get("pidx")}
            else:
                error_message = "Payment failed. Please try again or contact support."
                return {"success": False, "message": error_message, "payment_id": response_data_json.get("pidx")}
            
        except (requests.RequestException, ValueError) as e:
            raise exceptions.APIException("Failed to verify payment. Please try again later.")
   