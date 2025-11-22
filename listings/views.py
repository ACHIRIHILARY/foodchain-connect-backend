from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import FoodListing
from .serializers import FoodListingSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class IsProviderOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.role == User.Role.ADMIN or request.user.is_staff:
            return True
        return obj.provider == request.user

class FoodListingViewSet(viewsets.ModelViewSet):
    queryset = FoodListing.objects.all()
    serializer_class = FoodListingSerializer
    permission_classes = (IsProviderOrAdminOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and (user.role == User.Role.ADMIN or user.is_staff):
            return FoodListing.objects.all()
        # Providers see their own, Seekers see available
        if user.is_authenticated and user.role == User.Role.PROVIDER:
            return FoodListing.objects.filter(provider=user)
        queryset = FoodListing.objects.filter(status=FoodListing.Status.AVAILABLE)
        
        # Filtering
        category = self.request.query_params.get('category')
        pickup_location = self.request.query_params.get('pickup_location')
        
        if category:
            queryset = queryset.filter(category=category)
        if pickup_location:
            queryset = queryset.filter(pickup_location__icontains=pickup_location)
            
        return queryset

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.PROVIDER and not self.request.user.is_staff:
             raise permissions.PermissionDenied("Only Providers can create listings.")
        serializer.save(provider=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        listing = self.get_object()
        listing.status = FoodListing.Status.AVAILABLE
        listing.save()
        return Response({'status': 'listing approved'})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def analytics(self, request):
        user = request.user
        if user.role != User.Role.PROVIDER:
            return Response({'error': 'Only Providers can view analytics'}, status=403)
        
        listings = FoodListing.objects.filter(provider=user)
        total_listings = listings.count()
        active_listings = listings.filter(status=FoodListing.Status.AVAILABLE).count()
        
        # Simple analytics
        return Response({
            'total_listings': total_listings,
            'active_listings': active_listings,
            'total_meals_donated': 0, # Placeholder, would need to parse quantity or add a numeric field
            'impact_score': total_listings * 10 # Placeholder metric
        })

