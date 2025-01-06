from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.user.username

from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    uidb64 = models.CharField(max_length=64, blank=True, null=True)  # Store UID base64
    token = models.CharField(max_length=128, blank=True, null=True)  # Store token
    expires_at = models.DateTimeField(blank=True, null=True)  # Expiration time for the code and token
    request_token = models.UUIDField(default=uuid4, editable=False)  # Unique request token

    def __str__(self):
        return f"Reset Code for {self.user.email}"

    def is_expired(self):
        return timezone.now() > self.expires_at if self.expires_at else False

    def delete_if_expired_or_used(self, token_used=False):
        if self.is_expired() or token_used:
            self.delete()

