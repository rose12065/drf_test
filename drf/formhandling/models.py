from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    customer=1
    seller=2
    agent=3
    ROLE_CHOICES = (
          (customer, 'customer'),
          (seller, 'seller'),
          (agent, 'agent'),
      )
    email=models.EmailField(
        verbose_name='email address',
        max_length=225,
        unique=True
    )
    date_of_birth=models.DateField(default='2000-01-01')
    profile_picture = models.TextField(null=True, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True)

class Item(models.Model):
    category = models.CharField(max_length=255)
    subcategory = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()
