from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from BookingEngineApp.models import UserRegistration

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegistration
        # declearing fields to serialize 
        fields = ['username', 'email' , 'first_name', 'last_name', 'password']

    # encrypting the password
    def save(self, **kwargs):
        self.validated_data['password'] = make_password(self.validated_data['password'])
        super().save(**kwargs)
