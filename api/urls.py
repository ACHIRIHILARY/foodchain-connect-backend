from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('auth/signup/', views.SignupView.as_view(), name='auth-signup'),
    path('auth/login/', views.LoginView.as_view(), name='auth-login'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('auth/session/', views.SessionView.as_view(), name='auth-session'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # User management endpoints
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/profile/', views.UserUpdateView.as_view(), name='user-profile-update'),

    # Donation endpoints
    path('donations/', views.DonationListView.as_view(), name='donation-list'),
    path('donations/<int:pk>/', views.DonationDetailView.as_view(), name='donation-detail'),
    path('donations/<int:donation_id>/claim/', views.DonationClaimView.as_view(), name='donation-claim'),

    # Admin endpoints
    path('admin/users/', views.AdminUserCreateView.as_view(), name='admin-user-create'),
    path('admin/users/<int:user_id>/verification/', views.AdminUserVerificationView.as_view(), name='admin-user-verification'),
    path('admin/users/<int:user_id>/subscription/', views.AdminUserSubscriptionView.as_view(), name='admin-user-subscription'),
    path('admin/users/<int:pk>/', views.AdminUserDeleteView.as_view(), name='admin-user-delete'),
    path('admin/settings/', views.AdminSettingsView.as_view(), name='admin-settings'),

    # Dashboard endpoints
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
]
