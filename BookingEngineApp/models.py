from django.contrib.auth.models import AbstractUser
from django.db import models


#  User Registration Model

class UserRegistration(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User')
    )

    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=4, null=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return self.username


# Upload Rooms Model

class Facility(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
         verbose_name = "Facility"
         verbose_name_plural = "Facilities"

    def __str__(self):
        return self.name

class RoomCategory(models.Model):
     type = models.CharField(max_length=100)

     class Meta:
         verbose_name = "Room Category"
         verbose_name_plural = "Room Categories"

class Room(models.Model):
    number = models.IntegerField(primary_key=True)
    price = models.IntegerField() 
    type = models.ForeignKey(RoomCategory,on_delete=models.CASCADE, null = True)
    description = models.TextField()
    facility = models.ManyToManyField(Facility)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return str(self.number)
   
class RoomImage(models.Model):
    number = models.ForeignKey(Room,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='rooms_images/')


# Upload Package Backend

class Package(models.Model):
     type = models.CharField(max_length=100)
     overview = models.TextField()
     description = models.TextField()
     is_booked = models.BooleanField(default=True)

     def __str__(self):
        return self.type

# Book Rooms Models

class Booking(models.Model):
     username = models.ForeignKey(UserRegistration,on_delete=models.CASCADE)
     type = models.ForeignKey(RoomCategory,on_delete=models.CASCADE)
     room = models.ForeignKey(Room,on_delete=models.CASCADE, null=True)
     check_in = models.DateField()
     check_out = models.DateField()

     def __str__(self):
        return str(self.room)