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
