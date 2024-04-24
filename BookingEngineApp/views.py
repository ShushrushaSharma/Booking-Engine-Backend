from itertools import count
from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.decorators import APIView
from BookingEngineApp.models import UserRegistration
from BookingEngineApp.serializers import UserRegisterSerializer, UserLoginSerializer, RoomSerializer, ResetPasswordSerializer, PackageSerializer, \
     VerifyAccountSerializer, BookingSerializer, ProfileSerializer, RoomCategorySerializer, FacilitySerializer, ContactSerializer, KhaltiSerializer, \
     KhaltiSerializerAfterInitiate, PaymentHistorySerializer, NotificationSerializer, SendPasswordResetEmailSerializer, ForgotPasswordSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from BookingEngineApp.models import Room, RoomCategory, Facility, UserRegistration, Package, Booking, Contact, PaymentHistory, Notification
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from BookingEngineApp.emails import send_otp_via_email, send_query_reply
from rest_framework import status
from datetime import datetime
from django.db import transaction
from rest_framework.parsers import MultiPartParser
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework.response import Response
import calendar
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import ExtractMonth


# User Register

class UserRegister(APIView):

    def post(self,request):
        serializer = UserRegisterSerializer(data = request.data)
        if serializer.is_valid():

            # validating username

            username = request.data.get('username')
            if UserRegistration.objects.filter(username=username).exists():
                return Response(serializer.errors, status=400)
                
            
            serializer.save()
            send_otp_via_email(serializer.data['email'])
            return Response(serializer.data, status= 201)
        return Response(serializer.errors, status=400)


# Verify OTP

class VerifyOTP(APIView):

    def post(self,request):
        print(request.data)
        serializer = VerifyAccountSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.data['email']
            otp = serializer.data['otp']

            user = UserRegistration.objects.filter(email=email)

            if not user.exists():
                print("user doesnot exist")
                return Response("Invalid Email!", status=400)
                
            
            if user[0].otp != otp:
                print("OTP invalid")
                return Response("Invalid OTP!", status=400)
                
            user = user.first()
            user.is_verified = True
            user.save()
            return Response("Account Verified.", status=200)

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
            
            if not user.is_verified:
                send_otp_via_email(user.email)
                return Response({'message':"Email not Verified", "email": user.email}, status=403)
            
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

    parser_classes = [MultiPartParser]

    def post(self, request):
        type = request.data.get('type')
        serializer = RoomCategorySerializer(data=request.data, context={'type': type})

        if serializer.is_valid():
            serializer.save()

             # creating notifications

            users = UserRegistration.objects.all().exclude(email__endswith = '@admin.com')
        
            # creating notifications for each user
            
            for user in users:
                Notification.objects.create(
                    username=user,
                    message=f"New Room Category named {type} was added."
                )
            
            print("Notifications sent to all users")

            return Response({'message': 'Room Category added successfully.', 'data': serializer.data}, status=201)
        
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

    parser_classes = [MultiPartParser]

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

    parser_classes = [MultiPartParser]

    def post(self, request):
        name = request.data.get('name')
        serializer = RoomSerializer(data=request.data,context={'name': name})
        if serializer.is_valid():

            # extracting validated data
            price = serializer.validated_data['price'] 
            sleeps = serializer.validated_data['sleeps']

            # calculating booking rewards and required points for loyalty
            credits_received = price * 10/100
            credits_required = price * sleeps

            # saving data with calculated credit points
            serializer.save(credits_received=credits_received, credits_required=credits_required)

            # creating notifications

            users = UserRegistration.objects.all().exclude(email__endswith = '@admin.com')
        
            # creating notifications for each user
            
            for user in users:
                Notification.objects.create(
                    username=user,
                    message=f"New Room named {name} was added."
                )
            
            print("Notifications sent to all users")
            
            return Response({'message': 'Room added successfully.', 'data': serializer.data}, status=201)
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

    parser_classes = [MultiPartParser]

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

    parser_classes = [MultiPartParser]

    def post(self, request):
        name = request.data.get('name')
        serializer = FacilitySerializer(data=request.data, context = {'name': name})

        if serializer.is_valid():
            facility_name = request.data.get('name')
            if Facility.objects.filter(name=facility_name).exists():
                return Response(serializer.errors, status=400)
            
            serializer.save()

            # creating notifications

            users = UserRegistration.objects.all().exclude(email__endswith = '@admin.com')
        
            # creating notifications for each user

            for user in users:
                Notification.objects.create(
                    username=user,
                    message=f"New Facility named {name} was added."
                )
            
            print("Notifications sent to all users")

            return Response({'message': 'Facility added successfully.', 'data': serializer.data}, status=201)
        
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

    def get(self,request):
        userregistration = UserRegistration.objects.exclude(email__endswith = '@admin.com')
        serializer = UserRegisterSerializer(userregistration, many = True)
        return Response(serializer.data)
    

class DeleteUserDetails(APIView):

    def delete(self,request,id):
        user = get_object_or_404(UserRegistration, id=id)
        user.delete()
        return Response("Deleted Successfully") 


# View Personal Details

class ViewPersonalDetails(APIView):

    def get(self,request,id):
        userregistration = get_object_or_404(UserRegistration,id = id)
        serializer = UserRegisterSerializer(userregistration, many = False)
        return Response(serializer.data)
    

# Update Personal Details

class UpdatePersonalDetails(APIView):

    parser_classes = [MultiPartParser]

    def patch(self,request,id):
        userregistration = get_object_or_404(UserRegistration,id=id)
        serializer = ProfileSerializer(instance = userregistration, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)    
    

# Reset your Password

class ResetPassword(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = ResetPasswordSerializer(data = request.data)
        if serializer.is_valid():
            # retriving user associated with this request
            user = request.user
            if user.check_password(serializer.data.get('oldpassword')):
                user.set_password(serializer.data.get('newpassword'))
                user.save()
                return Response({'message': 'Password changed successfully.'}, status=200)
            return Response({'error': 'Invalid Old Password!'}, status=400)
        return Response(serializer.errors, status=400)
    

# Forgot Password

class SendPasswordResetEmailView(APIView):
    def post(self, request):
        serializer = SendPasswordResetEmailSerializer(data = request.data)
        if serializer.is_valid():
            return Response("Password Reset Link Sent.", status= 201)
        print(serializer.errors)
        return Response(serializer.errors, status= 400)


class ResetPasswordView(APIView):
    def post(self, request, uid, token):
        serializer = ForgotPasswordSerializer(data = request.data, context ={"uid": uid, "token":token})
        if serializer.is_valid():
            return Response("Password Reset Successfully.", status=200)
        return Response(serializer.errors, status=400)


# Upload Packages in Admin Panel

class AddPackage(APIView):

    parser_classes = [MultiPartParser]

    def post(self,request):
        type = request.data.get('type')

        serializer = PackageSerializer(data=request.data, context={'type': type})

        if serializer.is_valid():

            # extracting validated data
            days = serializer.validated_data['days'] 

            if 'room' not in serializer.validated_data:
                return Response({'message': 'Room data is missing'}, status=400)
            
            room = serializer.validated_data['room']
            room_price = room.price
            total_price = room_price * days

            serializer.validated_data['price'] = total_price
            serializer.save()

            # creating notifications

            users = UserRegistration.objects.all().exclude(email__endswith = '@admin.com')
        
            # creating notifications for each user
            
            for user in users:
                Notification.objects.create(
                    username=user,
                    message=f"New Package named {type} was added."
                )
            
            print("Notifications sent to all users")

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

    parser_classes = [MultiPartParser]

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

class AddContact(APIView):

    def post(self,request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

class ShowContact(APIView):

    def get(self,request):
        contact = Contact.objects.all()
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data,status=200)


class DeleteContact(APIView):

    def delete(self,request,id):
        contact = get_object_or_404(Contact, id=id)
        contact.delete()
        return Response("Deleted Successfully") 
    
class SendQueryReply(APIView):
    
    def post(self, request):
        data = request.data
        email = data.get('email')
        reply = data.get('reply')

        if not email:
            return Response({'error': 'Email address is required.'}, status=400)

        if not reply:
            return Response({'error': 'Reply content is required.'}, status=400)

        try:
            contact = Contact.objects.get(email=email)
        except Contact.DoesNotExist:
            return Response({'error': 'No contact found with the provided email address.'}, status=404)

        success, message = send_query_reply(email=email, reply=reply)

        if success:
            contact.reply = reply
            contact.save()
            return Response({'message': message}, status=200)
        else:
            return Response({'error': message}, status=500)
    

# Notifications

class GetNotificationsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # fetching notifications associated with the current user

        notifications = Notification.objects.filter(username=request.user).order_by('-date')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=200)


class CountUnseenNotificationsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # counting unseen notifications for the current user

        count = Notification.objects.filter(username=request.user, seen=False).count()
        return Response({'count': count}, status=200)


class SeeNotificationsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # marking unseen notifications as seen for the current user

        notifications = Notification.objects.filter(username=request.user, seen=False)
        for notification in notifications:
            notification.seen = True
            notification.save()
        return Response("Notifications Seen.", status=200)


# Book Rooms

class LoyaltyBookings(APIView):

    permission_classes = [IsAuthenticated]

    parser_classes = [MultiPartParser]

    def post(self, request):

        serializer = BookingSerializer(data=request.data)

        if serializer.is_valid():
            room_name = serializer.data['name']
            check_in = serializer.data['check_in']
            check_out = serializer.data['check_out']
            adult = serializer.data['adult']
            children = serializer.data['children']

            # checking if booking already exists

            if Booking.objects.filter(name=room_name, check_in=check_in, check_out=check_out).exists():
                return Response({'message': 'Booking already exists.'}, status=400)

            # checking if checkout date is before checkin date

            if check_out < check_in:
                return Response({'message': 'Checkout date must be after check-in date.'}, status=400)

            try:
                room = Room.objects.get(number=room_name)
            except Room.DoesNotExist:
                return Response({'message': 'Room cannot be found.'}, status=400)

            if not self.is_room_available(room, check_in, check_out):
                return Response({'message': 'Specified room is not available for the given dates.'}, status=400)

            # calculating price with the duration of stay

            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            duration_of_stay = max((check_out_date - check_in_date).days, 1)
            total_price = room.price * duration_of_stay
            grand_total = total_price + (13 / 100 * total_price)

            # calculating occupancy

            occupancy = adult + children

            # verifying occupancy and no of sleeps in the room

            if room.sleeps < occupancy:
                return Response({'message': 'Occupancy is more than a limit.'}, status=400)

            # booking rewards and booking credits for a room

            booking_rewards = room.credits_received
            booking_credits = room.credits_required

            # updating user's total booking rewards with loyalty

            user_registration = UserRegistration.objects.get(username=request.user)
            if user_registration.total_bookings_rewards >= booking_credits:
                with transaction.atomic():
                    user_registration.total_bookings_rewards -= booking_credits
                    booking_credits = 0
                    user_registration.save()
            else:
                return Response({'message': 'Insufficient booking rewards to make loyalty payment.'}, status=400)

            user_registration.total_bookings_rewards += booking_rewards
            user_registration.save()

            # creating bookings

            booking = Booking.objects.create(
                username=self.request.user,
                name=room,
                check_in=check_in,
                check_out=check_out,
                adult=adult,
                children=children,
                stay_duration=duration_of_stay,
                occupancy=occupancy,
                total_price=total_price,
                grand_total=grand_total,
                booking_rewards=booking_rewards,
                booking_credits=booking_credits
            )
            booking.save()
            room.save()

            return Response({'message': f'Room {room} booked successfully.'}, status=201)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # checking the available rooms with the specific dates

    def is_room_available(self, room, check_in, check_out):
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

        booking_list = Booking.objects.filter(name=room)
        for booking in booking_list:
            if booking.check_in < check_out_date and booking.check_out > check_in_date:
                return False
        return True
    

# calculating data for all the bookings
    
class CalculatePrice(APIView):

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            room_name = serializer.data['name']
            check_in = serializer.data['check_in']
            check_out = serializer.data['check_out']
            adult = serializer.data['adult']
            children = serializer.data['children']

            if Booking.objects.filter(name=room_name, check_in=check_in, check_out=check_out).exists():
                    return Response({'message': 'Booking exists in same dates!'}, status=404)

            # checking if checkout date is before checkin date
            if check_out < check_in:
                return Response({'message': 'Checkout date must be after check-in date!'}, status=400)

            try:
                room = Room.objects.get(number=room_name)
            except Room.DoesNotExist:
                return Response({'error': 'Room cannot be found.'}, status=400)
            
            if not self.is_room_available(room, check_in, check_out):
                return Response({'message': 'Specified room is not available for the given dates!'}, status=404)

            # calculating price with the duration of stay
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            duration_of_stay = max((check_out_date - check_in_date).days, 1)

            total_price = room.price * duration_of_stay
            grand_total = total_price + (13/100 * total_price)

            # calculating occupancy
            occupancy = adult + children

            # verifying occupancy and no of sleeps in the room
            if room.sleeps < occupancy:
                return Response({'message': 'Occupancy is more than a limit!'}, status=400)

            return Response({
                'stay_duration': duration_of_stay,
                'total_price': total_price,
                'grand_total': grand_total,
                'occupancy': occupancy
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=400)
    
    # checking the available rooms with the specific dates

    def is_room_available(self, room, check_in, check_out):
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

        booking_list = Booking.objects.filter(name=room)
        for booking in booking_list:
            if booking.check_in < check_out_date and booking.check_out > check_in_date:
                return False
        return True


class ShowBookings(APIView):

    def get(self,request):
        booking = Booking.objects.filter(username = request.user)
        serializer = BookingSerializer(booking, many=True)
        return Response(serializer.data,status=200)
    

class ShowAllBookings(APIView):

    def get(self,request):
        booking = Booking.objects.all()
        serializer = BookingSerializer(booking, many=True)
        return Response(serializer.data,status=200)


class DeleteBookings(APIView):

    def delete(self,request,id):
        booking = get_object_or_404(Booking, id=id)
        booking.delete()
        return Response("Deleted Successfully") 


# Khalti Payments

class KhaltiApiView(APIView):

    parser_classes= [MultiPartParser]

    @extend_schema(
        operation_id="API to make a post request in Khalti",
        description="""
        This API is for making a POST request to Khalti,
        where it takes return_url, website_url, amount, purchase_order_id,appointment_id's
        purchase_order_name as compulsory request data.
        There are other optional request data like customer_info,
        amount_breakdown, product_details.
        """,
        request=KhaltiSerializer,
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="Khalti",
                fields={
                    "pidx": serializers.CharField(),
                    "payment_url": serializers.CharField(),
                    "expires_at": serializers.DateTimeField(),
                    "expires_in": serializers.IntegerField(),
                },
            )
        },
    )

    def post(self, request):
        serializer = KhaltiSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        khalti_data = serializer.save()

        # Save booking details after successful payment
        if khalti_data:
            booking_serializer = BookingSerializer(data = request.data)
            if booking_serializer.is_valid():

                room_name = booking_serializer.data['name']
                check_in = booking_serializer.data['check_in']
                check_out = booking_serializer.data['check_out']
                adult = booking_serializer.data['adult']
                children = booking_serializer.data['children']

                if Booking.objects.filter(name=room_name, check_in=check_in, check_out=check_out).exists():
                    return Response({'message': 'Booking already exists.'}, status=400)


                if check_out < check_in:
                    return Response({'message': 'Checkout date must be after check-in date.'}, status=400)

                try:
                    room = Room.objects.get(number=room_name)
                except Room.DoesNotExist:
                    return Response({'message': 'Room cannot be found.'}, status=400)

                if not self.is_room_available(room, check_in, check_out):
                    return Response({'message': 'Specified room is not available for the given dates.'}, status=400)

                # calculating price with the duration of stay

                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
                duration_of_stay = max((check_out_date - check_in_date).days, 1)
                total_price = room.price * duration_of_stay
                grand_total = total_price + (13 / 100 * total_price)

                # calculating occupancy

                occupancy = adult + children

                # verifying occupancy and no of sleeps in the room

                if room.sleeps < occupancy:
                    return Response({'message': 'Occupancy is more than a limit.'}, status=400)

                # booking rewards and booking credits for a room

                booking_rewards = room.credits_received
                booking_credits = room.credits_required

                # updating user's total booking rewards with loyalty

                user_registration = UserRegistration.objects.get(username=request.user)

                user_registration.total_bookings_rewards += booking_rewards
                user_registration.save()

                booking = Booking.objects.create(
                    username=self.request.user,
                    name=room,
                    check_in=check_in,
                    check_out=check_out,
                    adult=adult,
                    children=children,
                    stay_duration=duration_of_stay,
                    occupancy=occupancy,
                    total_price=total_price,
                    grand_total=grand_total,
                    booking_rewards=booking_rewards,
                    booking_credits=booking_credits
                )
                booking.save()
                room.save() 
                    
            else:
                return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Khalti data retrieved successfully", "data": khalti_data}, status=status.HTTP_200_OK)
    
    def is_room_available(self, room, check_in, check_out):
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

        booking_list = Booking.objects.filter(name=room)
        for booking in booking_list:
            if booking.check_in < check_out_date and booking.check_out > check_in_date:
                return False
        return True
    
    @extend_schema (
        operation_id="API to make a get request by khalti",
        description="""
        This api is for khalti to give get request after the payment is successfull ..
        """,
    )

    def get(self, request):
        serializer = KhaltiSerializerAfterInitiate(data=request.query_params, context={"request": request})
        serializer.is_valid(raise_exception=True)
        success = serializer.save()

        if success:
            success_url = settings.PAYMENT_SUCCESS_URL

            return HttpResponseRedirect(redirect_to=f"{success_url}?payment_id={id}")
        return HttpResponseRedirect(redirect_to=f"{settings.PAYMENT_FAILED_URL}?payment_id={id}")


# Khalti Payment For Packages

class PackagesApiView(APIView):

    @extend_schema(
        operation_id="API to make a post request in Khalti",
        description="""
        This API is for making a POST request to Khalti,
        where it takes return_url, website_url, amount, purchase_order_id, appointment_id's
        purchase_order_name as compulsory request data.
        There are other optional request data like customer_info,
        amount_breakdown, product_details.
        """,
        request=KhaltiSerializer,
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="Khalti",
                fields={
                    "pidx": serializers.CharField(),
                    "payment_url": serializers.CharField(),
                    "expires_at": serializers.DateTimeField(),
                    "expires_in": serializers.IntegerField(),
                },
            )
        },
    )

    def post(self, request):
        serializer = KhaltiSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        khalti_data = serializer.save()


        # Save booking details after successful payment

        if khalti_data:
            booking_serializer = BookingSerializer(data=request.data)

            if booking_serializer.is_valid():
                room_name = booking_serializer.data['name']
                package_id = booking_serializer.data['type']
                check_in = booking_serializer.data['check_in']
                check_out = booking_serializer.data['check_out']

                if Booking.objects.filter(name=room_name, check_in=check_in, check_out=check_out).exists():
                    return Response({'message': 'Booking already exists.'}, status=400)

                if check_out < check_in:
                    return Response({'message': 'Checkout date must be after check-in date.'}, status=400)

                try:
                    package = Package.objects.get(id=package_id)
                except Package.DoesNotExist:
                    return Response({'message': 'Package cannot be found.'}, status=400)

                if not self.is_room_available(package.room, check_in, check_out):
                    return Response({'message': 'Specified Package is not available for the given dates.'}, status=400)
                

                # verifying dates and days

                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
                duration_of_stay = max((check_out_date - check_in_date).days, 1)

                if duration_of_stay > package.days:
                    return Response({'message': 'Duration of Stay is more than the Limit.'}, status=400)

                # calculating price with the duration of stay
                
                total_price = package.price 
                grand_total = total_price + (13 / 100 * total_price)
                

                booking = Booking.objects.create(
                    username=self.request.user,
                    name=package.room,  
                    type=package,
                    check_in=check_in,
                    check_out=check_out,
                    stay_duration=package.days,
                    total_price=total_price,
                    grand_total=grand_total,
                )
                booking.save()

            else:
                return Response(booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Khalti data retrieved successfully", "data": khalti_data}, status=status.HTTP_200_OK)
    
    def is_room_available(self, room, check_in, check_out):
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

        booking_list = Booking.objects.filter(name=room)
        for booking in booking_list:
            if booking.check_in < check_out_date and booking.check_out > check_in_date:
                return False
        return True
    
    @extend_schema (
        operation_id="API to make a get request by khalti",
        description="""
        This api is for khalti to give get request after the payment is successfull ..
        """,
    )

    def get(self, request):
        serializer = KhaltiSerializerAfterInitiate(data=request.query_params, context={"request": request})
        serializer.is_valid(raise_exception=True)
        success = serializer.save()

        if success:
            success_url = settings.PAYMENT_SUCCESS_URL

            return HttpResponseRedirect(redirect_to=f"{success_url}?payment_id={id}")
        return HttpResponseRedirect(redirect_to=f"{settings.PAYMENT_FAILED_URL}?payment_id={id}")
    

# Show Payment History

class ShowPaymentHistory(APIView):

    def get(self,request):
        payment = PaymentHistory.objects.filter(username = request.user)
        serializer = PaymentHistorySerializer(payment, many=True)
        return Response(serializer.data,status=200)


# Admin Dashboard

class CountDetailsView(APIView):
    
    def get(self, request):
        rooms = Room.objects.all().count()
        users = UserRegistration.objects.exclude(email__endswith = '@admin.com').count()
        bookings = Booking.objects.all().count()

        return Response({
            'rooms': rooms, 'users': users, 'bookings': bookings
        }, status=200)


class TopBookingsView(APIView):

    def get(self, request):

        # getting the current year
        current_year = timezone.now().year

        # calculating the bookings count for each month of the current year
        bookings_by_month = Booking.objects.filter(check_in__year=current_year).annotate(
            month=ExtractMonth('check_in')).values('month').annotate(request_count=Count('id'))

        # organizing the data into a dictionary with month names as keys and trade request counts as values
        top_months_data = {}

        for entry in bookings_by_month:
            month_number = entry['month']
            month_name = calendar.month_name[month_number]  
            top_months_data[month_name] = entry['request_count']

        return Response(top_months_data, status=200)
    

class RoomCategoryDetails(APIView):

    def get(self, request):

        # retriving all room categories and count the number of rooms in each category
        room_categories = RoomCategory.objects.all()
        category_data = []

        for category in room_categories:
            room_count = Room.objects.filter(type=category).count()
            category_data.append({
                'category': category.type,
                'room_count': room_count
            })

        return Response(category_data)
    