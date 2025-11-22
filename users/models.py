from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        PROVIDER = 'PROVIDER', 'Provider'
        SEEKER = 'SEEKER', 'Seeker'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.SEEKER)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    verification_document = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"
