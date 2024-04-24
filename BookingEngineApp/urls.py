from django.urls import path
from .views import UserRegister, UserLogin, AddRooms, ShowRooms, UpdateRooms, DeleteRooms, ViewUserDetails, ViewPersonalDetails, UpdatePersonalDetails, \
ResetPassword, AddPackage, ShowPackage, UpdatePackage, DeletePackage, VerifyOTP, AddRoomsCategory, UpdateRoomsCategory, ShowRoomsCategory, DeleteUserDetails, \
DeleteRoomsCategory, AddFacilities, ShowFacilities, DeleteFacilities, UpdateFacilities, ShowSpecificRoomsCategory, ShowSpecificRoom, RoomCategoryDetails, \
ShowSpecificPackage, AddContact, ShowBookings, CalculatePrice, LoyaltyBookings, KhaltiApiView, PackagesApiView, CountDetailsView, TopBookingsView, ShowContact,\
DeleteContact, DeleteBookings, ShowPaymentHistory, GetNotificationsView, CountUnseenNotificationsView, SeeNotificationsView, SendQueryReply, ShowAllBookings, \
SendPasswordResetEmailView, ResetPasswordView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', UserRegister.as_view(), name = "register"),
    path('verifyotp/',VerifyOTP.as_view(),name="verify_otp"),
    path('login/',UserLogin.as_view(),name="login"),

    path('addrooms/',AddRooms.as_view(),name="add_rooms"),
    path('showrooms/',ShowRooms.as_view(),name="show_rooms"),
    path('updaterooms/<int:pk>/',UpdateRooms.as_view(),name="update_rooms"),
    path('deleterooms/<int:pk>/',DeleteRooms.as_view(),name="delete_rooms"),
    path('showspecificroom/<int:pk>/',ShowSpecificRoom.as_view(),name="showspecific_room"),

    path('addroomscategory/',AddRoomsCategory.as_view(),name="add_roomscategory"),
    path('showroomscategory/',ShowRoomsCategory.as_view(),name="show_roomscategory"),
    path('updateroomscategory/<int:pk>/',UpdateRoomsCategory.as_view(),name="update_roomscategory"),
    path('deleteroomscategory/<int:pk>/',DeleteRoomsCategory.as_view(),name="delete_roomscategory"),
    path('showspecificroomscategory/<int:pk>/',ShowSpecificRoomsCategory.as_view(),name="showspecific_roomscategory"),

    path('addfacilities/',AddFacilities.as_view(),name="add_facilities"),
    path('showfacilities/',ShowFacilities.as_view(),name="show_facilities"),
    path('updatefacilities/<int:pk>/',UpdateFacilities.as_view(),name="update_facilities"),
    path('deletefacilities/<int:pk>/',DeleteFacilities.as_view(),name="delete_facilities"),

    path('viewuserdetails/',ViewUserDetails.as_view(),name="view_user_details"),
    path('deleteuserdetails/<int:id>/',DeleteUserDetails.as_view(),name="delete_user_details"),

    path('viewpersonaldetails/<int:id>/',ViewPersonalDetails.as_view(),name="view_personal_details"),
    path('updatepersonaldetails/<int:id>/',UpdatePersonalDetails.as_view(),name="update_personal_details"),

    path('resetpassword/',ResetPassword.as_view(),name="reset_password"),
    path("send_reset_password_email/",SendPasswordResetEmailView.as_view(), name="reset-password-email"),
    path("reset_password/<str:uid>/<str:token>/",ResetPasswordView.as_view(), name="reset-password"),

    path('addpackage/',AddPackage.as_view(),name="add_package"),
    path('showpackage/',ShowPackage.as_view(),name="show_package"),
    path('updatepackage/<int:id>/',UpdatePackage.as_view(),name="update_package"),
    path('deletepackage/<int:id>/',DeletePackage.as_view(),name="delete_package"),
    path('showspecificpackage/<int:id>/',ShowSpecificPackage.as_view(),name="showspecific_package"),

    path('addcontact/',AddContact.as_view(),name="add_contact"),
    path('showcontact/',ShowContact.as_view(),name="show_contact"),
    path('deletecontact/<int:id>/',DeleteContact.as_view(),name="delete_contact"),
    path('sendqueryreply/',SendQueryReply.as_view(),name="query_reply"),

    path('loyaltybookings/',LoyaltyBookings.as_view(),name="loyalty_bookings"),
    path('calculatetotals/',CalculatePrice.as_view(),name="calculate_price"),
    path('showbookings/',ShowBookings.as_view(),name="show_bookings"),
    path('showallbookings/',ShowAllBookings.as_view(),name="showall_bookings"),
    path('deletebookings/<int:id>/',DeleteBookings.as_view(),name="delete_bookings"),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("khalti-initiate/", KhaltiApiView.as_view(), name="khalti-initiate"),
    path("package-initiate/", PackagesApiView.as_view(), name="package-initiate"),
    path("paymenthistory/", ShowPaymentHistory.as_view(), name="payment-history"),

    path("count-details/", CountDetailsView.as_view(), name="count-details"),
    path("booking-details/", TopBookingsView.as_view(), name="booking-details"),
    path("category-details/", RoomCategoryDetails.as_view(), name="category-details"),  

    path("notifications/", GetNotificationsView.as_view(), name="notifications"),
    path("unseennotifications/", CountUnseenNotificationsView.as_view(), name="notifications"),
    path("seenotifications/", SeeNotificationsView.as_view(), name="notifications"),

]
