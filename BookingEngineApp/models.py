from django.contrib.auth.models import AbstractUser
from django.db import models


#  User Registration Model

class UserRegistration(AbstractUser):

    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=4, null=True)
    profile_picture = models.ImageField(upload_to="profile_images/", blank=True, null=True, default="profile_images/defaultimage.png")
    total_bookings_rewards = models.IntegerField()

    def __str__(self):
        return self.username


# Upload Rooms Model

class Facility(models.Model):
    name = models.CharField(max_length=100,unique=True)

    class Meta:
         verbose_name = "Facility"
         verbose_name_plural = "Facilities"

    def __str__(self):
        return self.name


class RoomCategory(models.Model):
     type = models.CharField(max_length=100, unique=True)
     image = models.ImageField(upload_to='category_images/')
     description = models.TextField()

     class Meta:
         verbose_name = "Room Category"
         verbose_name_plural = "Room Categories"
    
     def __str__(self):
        return self.type


class Room(models.Model):
    number = models.IntegerField(primary_key=True)
    price = models.IntegerField() 
    name = models.CharField(max_length=100,unique=True)
    type = models.ForeignKey(RoomCategory,on_delete=models.CASCADE, null = True)
    image = models.ImageField(upload_to='rooms_images/')
    facility = models.ManyToManyField(Facility, related_name='rooms')
    sleeps = models.IntegerField()
    credits_received = models.IntegerField()
    credits_required = models.IntegerField()

    def __str__(self):
        return str(self.name)
   

# Upload Package Backend    

class Package(models.Model):
     type = models.CharField(max_length=100)
     overview = models.TextField()
     description = models.TextField()
     credits_received = models.IntegerField()
     credits_required = models.IntegerField()
     is_booked = models.BooleanField(default=False)

     def __str__(self):
        return self.type


# Book Rooms Models

class Booking(models.Model):
     username = models.ForeignKey(UserRegistration,on_delete=models.CASCADE)
     name = models.ForeignKey(Room,on_delete=models.CASCADE, null=True)

     check_in = models.DateField()
     check_out = models.DateField()
     adult = models.IntegerField(default = 1)
     children = models.IntegerField(default = 0)

     stay_duration = models.IntegerField()
     occupancy = models.IntegerField()
     total_price = models.IntegerField()
     grand_total = models.IntegerField()
     booking_rewards = models.IntegerField()
     booking_credits = models.IntegerField()

     def __str__(self):
        return str(self.name)
     

# Contact Models

class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length = 100) 
    subject = models.CharField(max_length=200)
    message = models.TextField()

    def __str__(self):
        return str(self.first_name)