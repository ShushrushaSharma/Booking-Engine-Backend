from django.urls import path
from .views import UserRegister, UserLogin, AddRooms, ShowRooms, UpdateRooms, DeleteRooms, ViewUserDetails, ViewPersonalDetails, UpdatePersonalDetails, ResetPassword, AddPackage, ShowPackage, UpdatePackage, DeletePackage, VerifyOTP, BookRooms

urlpatterns = [
    path('register/', UserRegister.as_view(), name = "register"),
    path('verifyotp/',VerifyOTP.as_view(),name="verify_otp"),
    path('login/',UserLogin.as_view(),name="login"),

    path('addrooms/',AddRooms.as_view(),name="add_rooms"),
    path('showrooms/',ShowRooms.as_view(),name="show_rooms"),
    path('updaterooms/<int:pk>/',UpdateRooms.as_view(),name="update_rooms"),
    path('deleterooms/<int:pk>/',DeleteRooms.as_view(),name="delete_rooms"),

    path('viewuserdetails/',ViewUserDetails.as_view(),name="view_user_details"),

    path('viewpersonaldetails/<int:id>/',ViewPersonalDetails.as_view(),name="view_personal_details"),
    path('updatepersonaldetails/<int:id>/',UpdatePersonalDetails.as_view(),name="update_personal_details"),

    path('resetpassword/',ResetPassword.as_view(),name="reset_password"),

    path('addpackage/',AddPackage.as_view(),name="add_package"),
    path('showpackage/',ShowPackage.as_view(),name="show_package"),
    path('updatepackage/<int:id>/',UpdatePackage.as_view(),name="update_package"),
    path('deletepackage/<int:id>/',DeletePackage.as_view(),name="delete_package"),

    path('bookrooms/',BookRooms.as_view(),name="book_rooms")

]

