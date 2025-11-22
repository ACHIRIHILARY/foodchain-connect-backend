from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FoodListingViewSet

router = DefaultRouter()
router.register(r'', FoodListingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
