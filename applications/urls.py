from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FoodApplicationViewSet

router = DefaultRouter()
router.register(r'', FoodApplicationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
