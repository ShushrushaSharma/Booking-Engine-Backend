from django.urls import path
from .views import UserRegister, UserLogin, AddRooms, ShowRooms, UpdateRooms, DeleteRooms, ViewPersonalDetails

urlpatterns = [
path('register/', UserRegister.as_view(), name = "register"),
path('login/',UserLogin.as_view(),name="login"),

path('addrooms/',AddRooms.as_view(),name="add_rooms"),
path('showrooms/',ShowRooms.as_view(),name="show_rooms"),
path('updaterooms/<int:pk>/',UpdateRooms.as_view(),name="update_rooms"),
path('deleterooms/<int:pk>/',DeleteRooms.as_view(),name="delete_rooms"),

 path('viewpersonaldetails/<int:id>/',ViewPersonalDetails.as_view(),name="view_personal_details"),
]
