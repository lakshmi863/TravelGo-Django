from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Flight, Booking, FoodOrder

# This registers your models so they appear in the Admin screenshot you sent
@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('airline', 'origin', 'destination', 'price')
    search_fields = ('origin', 'destination', 'airline')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('passenger_name', 'flight', 'status', 'seat_number')
    list_filter = ('status',)

admin.site.register(FoodOrder)