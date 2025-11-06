from rest_framework import permissions


class IsAdminOrMainAdmin(permissions.BasePermission):
    """
    Custom permission to only allow Admin or Main Admin users to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['Admin', 'Main Admin']


class IsMainAdmin(permissions.BasePermission):
    """
    Custom permission to only allow Main Admin users to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'Main Admin'


class IsDonor(permissions.BasePermission):
    """
    Custom permission to only allow Donor users to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'Donor'


class IsReceiver(permissions.BasePermission):
    """
    Custom permission to only allow Receiver users to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'Receiver'


class IsDonorOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow Donor or Admin users to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['Donor', 'Admin', 'Main Admin']


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or Admin users to access.
    """
    def has_object_permission(self, request, view, obj):
        # Allow if user is admin
        if request.user.role in ['Admin', 'Main Admin']:
            return True

        # Allow if user is the owner (for donations, check donor field)
        if hasattr(obj, 'donor'):
            return obj.donor == request.user

        # Allow if user is the owner (for users, check if it's their own profile)
        if hasattr(obj, 'id'):
            return obj.id == request.user.id

        return False


class CanClaimDonation(permissions.BasePermission):
    """
    Custom permission to only allow Receiver users to claim donations.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'Receiver'


class CanDeleteUser(permissions.BasePermission):
    """
    Custom permission for user deletion based on roles.
    Main Admin can delete anyone except themselves.
    Admin can delete Donor/Receiver but not other Admin/Main Admin.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Main Admin can delete anyone except themselves
        if request.user.role == 'Main Admin':
            return obj.id != request.user.id

        # Admin can delete Donor and Receiver roles, but not other Admin/Main Admin
        if request.user.role == 'Admin':
            return obj.role in ['Donor', 'Receiver']

        return False
