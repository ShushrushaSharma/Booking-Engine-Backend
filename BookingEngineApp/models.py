from django.contrib.auth.models import AbstractUser
from django.db import models

class UserRegistration(AbstractUser):
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

def __str__(self):
        return self.username

# Upload Rooms Models

class Facility(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
         verbose_name = "Facility"
         verbose_name_plural = "Facilities"

class Room(models.Model):
    number = models.IntegerField(primary_key=True)
    price = models.IntegerField() 
    type = models.CharField(max_length=100)
    description = models.TextField()
    facility = models.ManyToManyField(Facility)
    is_booked = models.BooleanField(default=False)
   
class RoomImage(models.Model):
    number = models.ForeignKey(Room,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='rooms_images/')

# Upload Package Backend

class Package(models.Model):
     type = models.CharField(max_length=100)
     overview = models.TextField()
     description = models.TextField()
     is_booked = models.BooleanField(default=True)