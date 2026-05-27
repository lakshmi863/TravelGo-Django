from django.db import models
from django.utils import timezone
import datetime
from decimal import Decimal  # <--- CRITICAL: Always use Decimal for money

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
    
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    flight_departure_datetime = models.DateTimeField(null=True) 

    def __str__(self):
        return f"{self.passenger_name} - {self.status} ({self.seat_number})"

    # --- CANCELLATION & REFUND LOGIC ---

    @property
    def can_cancel(self):
        """
        HARD RULE: Cannot cancel if the flight is less than 4 hours away.
        """
        if not self.flight_departure_datetime:
            return False
        
        now = timezone.now()
        # Returns True only if departure is > 4 hours from right now
        return self.flight_departure_datetime > (now + datetime.timedelta(hours=4))

    def calculate_refund_amount(self):
        """
        FINANCIAL LOGIC:
        1. If cancelled within 24h of booking -> 100% Refund
        2. If cancelled after 24h of booking -> 70% Refund
        3. If window is closed -> 0 Refund
        """
        if not self.can_cancel:
            return Decimal('0.00')

        now = timezone.now()
        time_since_booking = (now - self.created_at).total_seconds()
        
        if time_since_booking < 86400:  # 86400 seconds = 24 hours
            return self.total_price * Decimal('1.0')
        else:
            return self.total_price * Decimal('0.7')

    @property
    def refund_policy_text(self):
        """
        Returns the human-readable string for emails and UI.
        """
        if not self.can_cancel:
            return "No Refund (Cancellation window closed)"
        
        now = timezone.now()
        diff = (now - self.created_at).total_seconds()
        
        if diff < 86400:
            return "100% Full Refund"
        return "70% Partial Refund"


class FoodOrder(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='food_orders', null=True)
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
    flight_inclusion = models.CharField(max_length=255)
    hotel_inclusion = models.CharField(max_length=255)

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