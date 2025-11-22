from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class FoodListing(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        PENDING = 'PENDING', 'Pending'
        COLLECTED = 'COLLECTED', 'Collected'
        EXPIRED = 'EXPIRED', 'Expired'

    class Category(models.TextChoices):
        COOKED = 'COOKED', 'Cooked Meal'
        PACKAGED = 'PACKAGED', 'Packaged Food'
        FRESH = 'FRESH', 'Fresh Produce'
        OTHER = 'OTHER', 'Other'

    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    quantity = models.CharField(max_length=100)
    expiry_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    pickup_location = models.TextField(blank=True, null=True)
    pickup_time_window = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='listings/', blank=True, null=True)

    def __str__(self):
        return self.title
