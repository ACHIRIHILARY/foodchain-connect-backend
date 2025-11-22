from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FoodApplication
from .serializers import FoodApplicationSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class IsSeekerOrProviderOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN or request.user.is_staff:
            return True
        if request.user == obj.seeker:
            return True
        if request.user == obj.listing.provider:
            return True
        return False

class FoodApplicationViewSet(viewsets.ModelViewSet):
    queryset = FoodApplication.objects.all()
    serializer_class = FoodApplicationSerializer
    permission_classes = (IsSeekerOrProviderOrAdmin,)

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.ADMIN or user.is_staff:
            return FoodApplication.objects.all()
        if user.role == User.Role.PROVIDER:
            return FoodApplication.objects.filter(listing__provider=user)
        return FoodApplication.objects.filter(seeker=user)

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.SEEKER and not self.request.user.is_staff:
             raise permissions.PermissionDenied("Only Seekers can apply for food.")
        serializer.save(seeker=self.request.user)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        application = self.get_object()
        # Only provider can approve/reject
        if request.user != application.listing.provider and request.user.role != User.Role.ADMIN:
            return Response({'error': 'Not authorized'}, status=403)
        
        status = request.data.get('status')
        if status in [FoodApplication.Status.APPROVED, FoodApplication.Status.REJECTED, FoodApplication.Status.COLLECTED]:
            application.status = status
            application.save()
            return Response({'status': f'Application {status}'})
        return Response({'error': 'Invalid status'}, status=400)

    @action(detail=True, methods=['post'])
    def confirm_pickup(self, request, pk=None):
        application = self.get_object()
        if request.user != application.seeker:
             return Response({'error': 'Not authorized'}, status=403)
        
        if application.status == FoodApplication.Status.APPROVED:
            application.status = FoodApplication.Status.COLLECTED
            application.save()
            # Update listing status as well? Maybe not if quantity remains.
            # For simplicity, let's assume 1 application = 1 listing fully collected for now, or handle partials later.
            return Response({'status': 'Pickup confirmed'})
        return Response({'error': 'Application must be APPROVED to confirm pickup'}, status=400)
