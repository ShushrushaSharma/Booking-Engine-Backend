from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.decorators import APIView
from .serializers import UserRegisterSerializer
from rest_framework.response import Response

class UserRegister(APIView):

    def post(self,request):
        serializer = UserRegisterSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status= 201)
        return Response(serializer.errors, status=400)
