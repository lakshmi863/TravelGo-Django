from django.db import models
from django.utils import timezone  # <--- Added this
import datetime                    # <--- Added this

class Flight(models.Model):
    airline = models.CharField(max_length=100)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    special_offer = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.airline}: {self.origin} to {self.destination}"

class Booking(models.Model):
    flight = models.ForeignKey('Flight', on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=255)
    passenger_email = models.EmailField()
    passenger_phone = models.CharField(max_length=20)
    seat_number = models.CharField(max_length=10)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_location = models.CharField(max_length=255, blank=True)
    device_id = models.CharField(max_length=255, blank=True)
    
    # --- PAYMENT "SQUARING" FIELDS ---
    # 1. Start as PENDING. Only change to BOOKED after bank confirmation.
    status = models.CharField(
        max_length=20, 
        choices=[
            ('PENDING', 'Pending Payment'),
            ('BOOKED', 'Confirmed'),
            ('CANCELLED', 'Cancelled'),
            ('FAILED', 'Payment Failed')
        ],
        default='PENDING' 
    )
    
    # 2. Financial tracking IDs (Linking Django to the Bank)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    # 3. Timekeeping
    created_at = models.DateTimeField(auto_now_add=True)
    flight_departure_datetime = models.DateTimeField(null=True) 

    def __str__(self):
        return f"{self.passenger_name} - {self.status} ({self.seat_number})"

    @property
    def can_cancel(self):
        """Logic: Cannot cancel if the flight is less than 4 hours away"""
        if not self.flight_departure_datetime:
            return False
        
        now = timezone.now()
        # Flight time must be at least 4 hours in the future from now
        return self.flight_departure_datetime > (now + datetime.timedelta(hours=4))

    @property
    def refund_eligibility(self):
        """Logic: 100% Refund if cancelled within 24 hours of booking"""
        now = timezone.now()
        diff = (now - self.created_at).total_seconds()
        
        if diff < 86400: # 24 hours in seconds
            return "100% Full Refund"
        return "70% Partial Refund"
class FoodOrder(models.Model):
    # Relate it to a booking for better data integrity
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='food_orders', null=True)
    
    # Fields requested
    passenger_name = models.CharField(max_length=255)
    flight_number = models.CharField(max_length=100)
    seat_number = models.CharField(max_length=10)
    food_type = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food_type} for {self.passenger_name}"    


class TravelPackage(models.Model):
    CATEGORY_CHOICES = [
        ('HONEYMOON', 'Honeymoon Special'),
        ('HOLIDAY', 'Holiday Escape'),
        ('WEEKEND', 'Weekend Trip'),
        ('FAMILY', 'Family & Kids'),
        ('GROUP', 'Group Tours'),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField()
    flight_inclusion = models.CharField(max_length=255) # e.g. "Indigo Return Flight"
    hotel_inclusion = models.CharField(max_length=255)  # e.g. "5-Star Resort, 3 Nights"

    def __str__(self):
        return f"{self.title} ({self.category})"

class PackageBooking(models.Model):
    package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=255)
    passenger_email = models.EmailField()
    status = models.CharField(max_length=20, default='PENDING')
    local_transaction_id = models.CharField(max_length=100, blank=True)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.passenger_name} - {self.package.title}"        