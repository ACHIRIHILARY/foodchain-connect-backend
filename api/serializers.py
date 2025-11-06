from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, Donation, PlatformSettings


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'role', 'phone', 'address',
            'is_verified', 'subscription_status', 'created_at',
            'password', 'password_confirm'
        ]
        read_only_fields = ['id', 'created_at', 'is_verified', 'subscription_status']

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'role', 'phone', 'address',
            'is_verified', 'subscription_status', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'role', 'is_verified', 'subscription_status', 'created_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'phone', 'address']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class DonationSerializer(serializers.ModelSerializer):
    donor_info = serializers.SerializerMethodField()
    claimed_by_info = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = [
            'id', 'food_name', 'quantity', 'category', 'best_before_date',
            'status', 'donor_info', 'claimed_by_info', 'image_url',
            'image_hint', 'location_lat', 'location_lng', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'donor_info', 'claimed_by_info', 'created_at', 'updated_at']

    def get_donor_info(self, obj):
        return {
            'id': obj.donor.id,
            'name': obj.donor.name
        }

    def get_claimed_by_info(self, obj):
        if obj.claimed_by:
            return {
                'id': obj.claimed_by.id,
                'name': obj.claimed_by.name
            }
        return None

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def validate_best_before_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Best before date must be in the future")
        return value


class DonationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = [
            'food_name', 'quantity', 'category', 'best_before_date',
            'image', 'image_hint', 'location_lat', 'location_lng'
        ]

    def validate_best_before_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Best before date must be in the future")
        return value

    def create(self, validated_data):
        validated_data['donor'] = self.context['request'].user
        return super().create(validated_data)


class DonationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = [
            'food_name', 'quantity', 'category', 'best_before_date',
            'image', 'image_hint', 'location_lat', 'location_lng'
        ]

    def validate_best_before_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Best before date must be in the future")
        return value

    def validate_status(self, value):
        # Donors can only set status to 'Available'
        if self.context['request'].user.role != 'Donor' and value != 'Available':
            raise serializers.ValidationError("Only donors can modify donation status")
        return value


class PlatformSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformSettings
        fields = ['pro_plan_price', 'updated_at']
        read_only_fields = ['updated_at']


class DashboardStatsSerializer(serializers.Serializer):
    active_donations = serializers.IntegerField()
    total_donations = serializers.IntegerField()
    claims_this_month = serializers.IntegerField()
