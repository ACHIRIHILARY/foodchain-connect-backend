from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout
from django.utils import timezone
from datetime import timedelta
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db import transaction
from asgiref.sync import sync_to_async
from .models import User, Donation, PlatformSettings
from .serializers import (
    UserSerializer, UserProfileSerializer, UserUpdateSerializer,
    LoginSerializer, DonationSerializer, DonationCreateSerializer,
    DonationUpdateSerializer, PlatformSettingsSerializer,
    DashboardStatsSerializer
)
from .permissions import (
    IsAdminOrMainAdmin, IsMainAdmin, IsDonor, IsReceiver,
    IsDonorOrAdmin, IsOwnerOrAdmin, CanClaimDonation, CanDeleteUser
)


# Authentication Views
class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': str(refresh.access_token),
            'refresh': str(refresh)
        })


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'})


class SessionView(APIView):
    def get(self, request):
        if request.user and request.user.is_authenticated:
            return Response({'user': UserProfileSerializer(request.user).data})
        return Response({'user': None})


# User Management Views
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminOrMainAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'is_verified', 'subscription_status']
    search_fields = ['name', 'email']


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# Donation Views
class DonationListView(generics.ListCreateAPIView):
    queryset = Donation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'donor']
    search_fields = ['food_name', 'quantity', 'category']
    ordering_fields = ['created_at', 'best_before_date']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DonationCreateSerializer
        return DonationSerializer

    def get_queryset(self):
        queryset = Donation.objects.all()
        status_filter = self.request.query_params.get('status')
        donor_id = self.request.query_params.get('donorId')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if donor_id:
            queryset = queryset.filter(donor_id=donor_id)

        return queryset


class DonationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Donation.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DonationUpdateSerializer
        return DonationSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsOwnerOrAdmin()]
        elif self.request.method in ['PUT', 'PATCH']:
            return [IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]


class DonationClaimView(APIView):
    permission_classes = [CanClaimDonation]

    def post(self, request, donation_id):
        donation = get_object_or_404(Donation, id=donation_id)

        if donation.status != 'Available':
            return Response(
                {'error': 'Donation is not available for claiming'},
                status=status.HTTP_400_BAD_REQUEST
            )

        donation.status = 'Claimed'
        donation.claimed_by = request.user
        donation.save()

        serializer = DonationSerializer(donation, context={'request': request})
        return Response(serializer.data)


# Admin Views
class AdminUserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsMainAdmin]


class AdminUserVerificationView(APIView):
    permission_classes = [IsAdminOrMainAdmin]

    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.is_verified = request.data.get('is_verified', user.is_verified)
        user.save()

        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


class AdminUserSubscriptionView(APIView):
    permission_classes = [IsAdminOrMainAdmin]

    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.subscription_status = request.data.get('subscription_status', user.subscription_status)
        user.save()

        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


class AdminUserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [CanDeleteUser]


class AdminSettingsView(generics.RetrieveUpdateAPIView):
    queryset = PlatformSettings.objects.all()
    serializer_class = PlatformSettingsSerializer
    permission_classes = [IsMainAdmin]

    def get_object(self):
        # Get or create the singleton settings object
        obj, created = PlatformSettings.objects.get_or_create(id=1)
        return obj


# Dashboard Views
class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if user.role in ['Donor', 'Admin', 'Main Admin']:
            # For donors: active donations, total donations, claims this month
            active_donations = Donation.objects.filter(
                donor=user,
                status='Available'
            ).count()

            total_donations = Donation.objects.filter(donor=user).count()

            claims_this_month = Donation.objects.filter(
                donor=user,
                status__in=['Claimed', 'PickedUp'],
                updated_at__gte=start_of_month
            ).count()

        elif user.role == 'Receiver':
            # For receivers: total claims, active claims
            active_donations = Donation.objects.filter(
                claimed_by=user,
                status='Claimed'
            ).count()

            total_donations = Donation.objects.filter(
                claimed_by=user
            ).count()

            claims_this_month = Donation.objects.filter(
                claimed_by=user,
                updated_at__gte=start_of_month
            ).count()

        else:
            active_donations = 0
            total_donations = 0
            claims_this_month = 0

        return Response({
            'active_donations': active_donations,
            'total_donations': total_donations,
            'claims_this_month': claims_this_month
        })
