from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.decorators import APIView
from BookingEngineApp.models import UserRegistration
from BookingEngineApp.serializers import UserRegisterSerializer, UserLoginSerializer, RoomSerializer, ResetPasswordSerializer, PackageSerializer, \
     VerifyAccountSerializer, BookingSerializer, ProfileSerializer, RoomCategorySerializer, FacilitySerializer, ContactSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from BookingEngineApp.models import Room, RoomCategory, Facility, UserRegistration, Package, Booking
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from BookingEngineApp.emails import send_otp_via_email
from rest_framework import status
from datetime import datetime


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
            
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'is_admin': user.is_superuser,
                'id': user.id
            }, status=200)
        
        return Response(serializer.errors, status=400)


# Upload Rooms Categories in admin panel

class AddRoomsCategory(APIView):

    def post(self, request):
        serializer = RoomCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ShowRoomsCategory(APIView):

    def get(self,request):
        roomscategory = RoomCategory.objects.all()
        serializer = RoomCategorySerializer(roomscategory, many = True)
        return Response(serializer.data)


class ShowSpecificRoomsCategory(APIView):

    def get(self,request,pk):
        roomscategory = get_object_or_404(RoomCategory, id=pk)
        serializer = RoomCategorySerializer(roomscategory, many = False)
        return Response(serializer.data)
   

class UpdateRoomsCategory(APIView):

    def patch(self,request,pk):
        roomscategory = get_object_or_404(RoomCategory,id = pk)
        serializer = RoomCategorySerializer(instance = roomscategory, data = request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class DeleteRoomsCategory(APIView):

    def delete(self,request,pk):
        roomscategory = get_object_or_404(RoomCategory, id = pk)
        roomscategory.delete()
        return Response("Deleted Successfully")


# Upload Rooms in admin panel

class AddRooms(APIView):

    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():

            # extracting validated data
            price = serializer.validated_data['price'] 
            sleeps = serializer.validated_data['sleeps']

            # calculating booking rewards and required points for loyalty
            credits_received = price / 2
            credits_required = price * sleeps

            # saving data with calculated credit points
            serializer.save(credits_received=credits_received, credits_required=credits_required)
            
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ShowRooms(APIView):

    def get(self,request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many = True)
        return Response(serializer.data)


class ShowSpecificRoom(APIView):

    def get(self,request,pk):
        rooms = get_object_or_404(Room, number=pk)
        serializer = RoomSerializer(rooms, many = False)
        return Response(serializer.data)
   

class UpdateRooms(APIView):

    def patch(self,request,pk):
        rooms = get_object_or_404(Room,number = pk)
        serializer = RoomSerializer(instance = rooms, data = request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class DeleteRooms(APIView):

    def delete(self,request,pk):
        rooms = get_object_or_404(Room, number = pk)
        rooms.delete()
        return Response("Deleted Successfully")


# Upload Facilities in admin panel

class AddFacilities(APIView):

    def post(self,request):
        serializer = FacilitySerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ShowFacilities(APIView):

    def get(self,request):
        facilities = Facility.objects.all()
        serializer = FacilitySerializer(facilities, many = True)
        return Response(serializer.data)
   

class UpdateFacilities(APIView):

    def patch(self,request,pk):
        facilities = get_object_or_404(Facility,id = pk)
        serializer = FacilitySerializer(instance = facilities, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class DeleteFacilities(APIView):

    def delete(self,request,pk):
        facilities = get_object_or_404(Facility, id = pk)
        facilities.delete()
        return Response("Deleted Successfully")


# View User Details

class ViewUserDetails(APIView):
    # permission_classes = [IsAdminUser]
    def get(self,request):
        userregistration = UserRegistration.objects.exclude(email__endswith = '@admin.com')
        serializer = UserRegisterSerializer(userregistration, many = True)
        return Response(serializer.data)


# View Personal Details

class ViewPersonalDetails(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self,request,id):
        userregistration = get_object_or_404(UserRegistration,id = id)
        serializer = UserRegisterSerializer(userregistration, many = False)
        return Response(serializer.data)
    

# Update Personal Details

class UpdatePersonalDetails(APIView):

    def patch(self,request,id):
        userregistration = get_object_or_404(UserRegistration,id=id)
        serializer = ProfileSerializer(instance = userregistration, data = request.data, partial = True)
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


class ShowSpecificPackage(APIView):

    def get(self,request,id):
        package = get_object_or_404(Package, id=id)
        serializer = PackageSerializer(package, many = False)
        return Response(serializer.data)
    

class UpdatePackage(APIView):

    def patch(self,request,id):
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


# Contact-Us

class Contact(APIView):

    def post(self,request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# Book Rooms

class BookRooms(APIView):

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            room_name = serializer.data['name']
            check_in = serializer.data['check_in']
            check_out = serializer.data['check_out']
            adult = serializer.data['adult']
            children = serializer.data['children']

            # checking if checkout date is before checkin date

            if check_out < check_in:
                return Response({'message': 'Checkout date must be after check-in date.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                room = Room.objects.get(number=room_name)
            except Room.DoesNotExist:
                return Response({'message': 'Specified room cannot be found or is already booked.'}, status=status.HTTP_400_BAD_REQUEST)

            if not self.is_room_available(room, check_in, check_out):
                return Response({'message': 'Specified room is not available for the given dates.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # calculating price with the duration of stay

            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            duration_of_stay = (check_out_date - check_in_date).days

            total_price = room.price * duration_of_stay

            grand_total = total_price + (13/100 * total_price)

            # calculating occupancy

            occupancy = adult + children

            # booking rewards and booking credits for a room

            booking_rewards = room.credits_received
            booking_credits = room.credits_required

            # creating bookings

            booking = Booking.objects.create(
                username=self.request.user,
                name=room,
                check_in=check_in,
                check_out=check_out,
                adult=adult,
                children=children,
                occupancy=occupancy,
                total_price=total_price,
                grand_total=grand_total,
                booking_rewards=booking_rewards,
                booking_credits=booking_credits
            )

            booking.save()
            room.save()

            return Response({'message': f'Room {room} booked successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # checking the available rooms with the sepecific dates

    def is_room_available(self, room, check_in, check_out):
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

        booking_list = Booking.objects.filter(name=room)
        for booking in booking_list:
            if booking.check_in < check_out_date and booking.check_out > check_in_date:
                return False
        return True
