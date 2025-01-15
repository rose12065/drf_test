from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from datetime import timedelta
from drf import settings

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
    category = models.CharField(max_length=255, null=True)
    subcategory = models.CharField(max_length=255, null=False)
    name = models.CharField(max_length=255, null=False)
    amount = models.PositiveIntegerField()
    
    
class APILog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_logs")
    api_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50)  # e.g., 'success' or 'failure'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.api_name} - {self.status}"
    
class LoginAttempt(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='login_attempt')
    failed_attempts = models.IntegerField(default=0)
    lockout_time = models.DateTimeField(null=True, blank=True)

    def is_locked_out(self):
        if self.lockout_time and now() < self.lockout_time:
            return True
        return False

    def reset_attempts(self):
        self.failed_attempts = 0
        self.lockout_time = None
        self.save()

    def increment_attempts(self):
        self.failed_attempts += 1
        if self.failed_attempts >= 3:
            self.lockout_time = now() + timedelta(minutes=15) 
        self.save()