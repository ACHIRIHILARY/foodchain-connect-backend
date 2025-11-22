from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlanViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'plans', PlanViewSet)
router.register(r'payments', PaymentViewSet, basename='payments')

urlpatterns = [
    path('', include(router.urls)),
]
