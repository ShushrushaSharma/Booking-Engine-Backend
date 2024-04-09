from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator


#  User Registration Model

class UserRegistration(AbstractUser):

    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(validators=[EmailValidator])
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=4, null=True)
    profile_picture = models.ImageField(upload_to="profile_images/", blank=True, null=True, default="profile_images/defaultimage.png")
    total_bookings_rewards = models.IntegerField(default = 0)

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
     type = models.CharField(max_length=100,unique=True)
     overview = models.TextField()
     days = models.IntegerField()
     room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
     price = models.IntegerField() 

     def __str__(self):
        return self.type


# Book Rooms Models

class Booking(models.Model):
     username = models.ForeignKey(UserRegistration,on_delete=models.CASCADE)
     name = models.ForeignKey(Room,on_delete=models.CASCADE, null=True)
     type = models.ForeignKey(Package, on_delete=models.CASCADE, null=True, blank=True)

     check_in = models.DateField()
     check_out = models.DateField()
     adult = models.IntegerField(default = 1)
     children = models.IntegerField(default = 0)

     stay_duration = models.IntegerField()
     occupancy = models.IntegerField(null=True)
     total_price = models.IntegerField()
     grand_total = models.IntegerField()
     booking_rewards = models.IntegerField(default=0)
     booking_credits = models.IntegerField(default=0)
     

     def __str__(self):
        return str(self.username)
     

# Payment History

class PaymentHistory(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    purchase_order_name = models.CharField(max_length=255)
    payment_id = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
         verbose_name = "Payment History"
         verbose_name_plural = "Payment History"

    def __str__(self):
        return f"{self.purchase_order_name} - {self.amount} - {self.status}"
     

# Contact Models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator])
    subject = models.CharField(max_length=200)
    message = models.TextField()

    def __str__(self):
        return str(self.name)
