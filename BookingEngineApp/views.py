from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.decorators import APIView
from BookingEngineApp.serializers import UserRegisterSerializer, UserLoginSerializer, RoomSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from BookingEngineApp.models import Room, UserRegistration
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated

class UserRegister(APIView):

    def post(self,request):
        serializer = UserRegisterSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status= 201)
        return Response(serializer.errors, status=400)


# User Login
class UserLogin(APIView):

    def post(self,request):
        serializer = UserLoginSerializer(data = request.data)
        if serializer.is_valid():
            # getting username and password 
            username = serializer.data['username']
            password = serializer.data['password']

            # authenticate user in database
            user = authenticate(username = username, password = password)

            if user is None:
                return Response("Invalid Credentials", status=400)
            
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        
        return Response(serializer.errors, status=400)
    

# Upload Rooms in admin panel

class AddRooms(APIView):

    def post(self,request):
        serializer = RoomSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ShowRooms(APIView):

    def get(self,request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many = True)
        return Response(serializer.data)
   
class UpdateRooms(APIView):

    def put(self,request,pk):
        rooms = get_object_or_404(Room,number = pk)
        serializer = RoomSerializer(instance = rooms, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

class DeleteRooms(APIView):

    def delete(self,request,pk):
        rooms = get_object_or_404(Room, number = pk)
        rooms.delete()
        return Response("Deleted Successfully")


# View User Details

class ViewPersonalDetails(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,id):
        userregistration = get_object_or_404(UserRegistration,id = id)
        serializer = UserRegisterSerializer(userregistration, many = False)
        return Response(serializer.data)


# Update Personal Details

class UpdatePersonalDetails(APIView):

    def put(self,request,id):
        useregisrtation = get_object_or_404(UserRegistration,id=id)
        serializer = UserRegisterSerializer(instance = useregisrtation, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)    
    
