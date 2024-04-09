from django.contrib import admin
from BookingEngineApp.models import UserRegistration, Room, Facility, Package, Booking, RoomCategory, Contact, PaymentHistory

# Register your models here.

admin.site.register(UserRegistration)
admin.site.register(RoomCategory)
admin.site.register(Room)
admin.site.register(Facility)
admin.site.register(Package)
admin.site.register(Booking)
admin.site.register(Contact)
admin.site.register(PaymentHistory)