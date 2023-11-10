from django.contrib import admin
from BookingEngineApp.models import UserRegistration, Room, RoomImage, Facility

# Register your models here.

admin.site.register(UserRegistration)
admin.site.register(Room)
admin.site.register(RoomImage)
admin.site.register(Facility)