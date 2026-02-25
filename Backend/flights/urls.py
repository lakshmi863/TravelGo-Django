from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FlightViewSet, BookingViewSet,FoodOrderViewSet # Add BookingViewSet here

router = DefaultRouter()
router.register(r'flights', FlightViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'food-orders', FoodOrderViewSet) # This creates /api/bookings/

urlpatterns = [
    path('', include(router.urls)),
]