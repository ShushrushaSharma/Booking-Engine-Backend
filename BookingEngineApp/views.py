from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.decorators import APIView
from BookingEngineApp.models import UserRegistration
from BookingEngineApp.serializers import UserRegisterSerializer, UserLoginSerializer, RoomSerializer, ResetPasswordSerializer, PackageSerializer, VerifyAccountSerializer, BookingSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from BookingEngineApp.models import Room, RoomCategory, UserRegistration, Package, Booking
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from BookingEngineApp.emails import send_otp_via_email


# User Register

class UserRegister(APIView):

    def post(self,request):
        serializer = UserRegisterSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            send_otp_via_email(serializer.data['email'])
            return Response(serializer.data, status= 201)
        return Response(serializer.errors, status=400)


# Verify OTP

class VerifyOTP(APIView):

    def post(self,request):
        serializer = VerifyAccountSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            otp = serializer.data['otp']

            user = UserRegistration.objects.filter(email=email)
            if not user.exists():
                return Response(
                    {
                        'status':'400',
                        'message':'Invalid Email'
                    }
                )
            
            if user[0].otp != otp:
                return Response(
                    {
                        'status':'400',
                        'message':'Invalid OTP'
                    }
                )
                
            user = user.first()
            user.is_verified = True
            user.save()
            return Response(
                    {
                        'status':'200',
                        'message':'account verified'
                    }
                )

        return Response(
                    {
                        'status':'400',
                        'data': serializer.errors
                    }
                )

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
            
            if not user.is_verified:
                return Response("Verify your account", status=401)
            
            # checking user role
            role = user.role
            
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': role,
            }, status=200)
        
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

class ViewUserDetails(APIView):
    permission_classes = [IsAdminUser]
    def get(self,request):
        userregistration = UserRegistration.objects.all()
        serializer = UserRegisterSerializer(userregistration, many = True)
        return Response(serializer.data)

# View Personal Details

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
    

# Reset your Password

class ResetPassword(APIView):
    def post(self,request):
        serializer = ResetPasswordSerializer(data = request.data)
        if serializer.is_valid():
            # retriving user associated with this request
            user = request.user
            if user.check_password(serializer.data.get('oldpassword')):
                user.set_password(serializer.data.get('newpassword'))
                user.save()
                return Response({'message': 'Password changed successfully.'}, status=200)
            return Response({'error': 'Invalid Old Password'}, status=400)
        return Response(serializer.errors, status=400)
    

# Upload Packages in Admin Panel

class AddPackage(APIView):

    def post(self,request):
        serializer = PackageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class ShowPackage(APIView):

    def get(self,request):
        package = Package.objects.all()
        serializer = PackageSerializer(package, many=True)
        return Response(serializer.data,status=200)
    
class UpdatePackage(APIView):

    def put(self,request,id):
        package = get_object_or_404(Package, id=id)
        serializer = PackageSerializer(instance=package, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    
class DeletePackage(APIView):

    def delete(self,request,id):
        package = get_object_or_404(Package, id=id)
        package.delete()
        return Response("Deleted Successfully")       
    

# Book Rooms

class BookRooms(APIView):

    def post(self,request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            room_type = serializer.data['type']
            check_in = serializer.data['check_in']
            check_out = serializer.data['check_out']

            room = Room.objects.filter(type = room_type).filter(is_booked = False).first()
            if not room:
                return Response({'message': 'No rooms of the specified category found.'})

            booking = Booking.objects.create(
                username = self.request.user,
                type = RoomCategory.objects.get(id = room_type),
                room = room,
                check_in = check_in,
                check_out = check_out
            )
            booking.save()
            room.is_booked = True
            room.save()

            return Response({'message': f'Room {room} booked successfully.'})
        return Response(serializer.errors, status=400)