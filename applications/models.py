from django.db import models
from django.contrib.auth import get_user_model
from listings.models import FoodListing

User = get_user_model()

class FoodApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        COLLECTED = 'COLLECTED', 'Collected'

    listing = models.ForeignKey(FoodListing, on_delete=models.CASCADE, related_name='applications')
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    message = models.TextField(blank=True)
    beneficiaries_count = models.IntegerField(default=0)
    preferred_pickup_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.seeker.username} - {self.listing.title}"
