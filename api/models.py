from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('Donor', 'Donor'),
        ('Receiver', 'Receiver'),
        ('Admin', 'Admin'),
        ('Main Admin', 'Main Admin'),
    ]

    SUBSCRIPTION_CHOICES = [
        ('Basic', 'Basic'),
        ('Pro', 'Pro'),
    ]

    name = models.CharField(max_length=255, help_text="User's full name or organization name")
    email = models.EmailField(unique=True, help_text="User's unique email address")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Donor', help_text="User's role in the system")
    phone = models.CharField(max_length=20, blank=True, help_text="User's contact phone number")
    address = models.TextField(blank=True, help_text="User's physical address")
    is_verified = models.BooleanField(default=False, help_text="Flag to indicate if the user is trusted")
    subscription_status = models.CharField(max_length=10, choices=SUBSCRIPTION_CHOICES, default='Basic', help_text="Determines access to premium features")
    created_at = models.DateTimeField(default=timezone.now, help_text="Server-side timestamp of when the user was created")

    # Override the default username field to not be required
    username = models.CharField(max_length=150, blank=True, null=True, unique=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"


class Donation(models.Model):
    CATEGORY_CHOICES = [
        ('Produce', 'Produce'),
        ('Baked Goods', 'Baked Goods'),
        ('Dairy', 'Dairy'),
        ('Meat', 'Meat'),
        ('Canned Goods', 'Canned Goods'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Claimed', 'Claimed'),
        ('PickedUp', 'PickedUp'),
        ('Expired', 'Expired'),
    ]

    food_name = models.CharField(max_length=255, help_text="Name of the food item")
    quantity = models.CharField(max_length=255, help_text="Description of the quantity")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, help_text="Category of the food item")
    best_before_date = models.DateTimeField(help_text="The best-before date for the food item")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available', help_text="Current status of the donation")
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations', help_text="The user who donated the item")
    claimed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='claimed_donations', help_text="The user who claimed the donation")
    image = models.ImageField(upload_to='donation_images/', blank=True, null=True, help_text="Photo of the donation")
    image_hint = models.CharField(max_length=255, blank=True, help_text="AI-powered image search keywords")
    location_lat = models.FloatField(null=True, blank=True, help_text="Latitude for geolocation")
    location_lng = models.FloatField(null=True, blank=True, help_text="Longitude for geolocation")
    created_at = models.DateTimeField(default=timezone.now, help_text="Server-side timestamp of when the donation was posted")
    updated_at = models.DateTimeField(auto_now=True, help_text="Server-side timestamp for the last update")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.food_name} - {self.donor.name} ({self.status})"


class PlatformSettings(models.Model):
    pro_plan_price = models.DecimalField(max_digits=10, decimal_places=2, default=10.00, help_text="The monthly price for the 'Pro' subscription")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Platform Setting"
        verbose_name_plural = "Platform Settings"

    def __str__(self):
        return f"Platform Settings (Pro Plan: ${self.pro_plan_price})"
