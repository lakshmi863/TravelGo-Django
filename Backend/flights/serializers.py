# flights/serializers.py
from rest_framework import serializers
from .models import Flight, Booking, FoodOrder

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    # --- Read-Only Flight Info ---
    flight_origin = serializers.ReadOnlyField(source='flight.origin')
    flight_destination = serializers.ReadOnlyField(source='flight.destination')
    flight_airline = serializers.ReadOnlyField(source='flight.airline')
    
    # --- NEW: Read-Only Cancellation & Refund Info ---
    # These pull directly from the @property methods in your models.py
    can_cancel = serializers.ReadOnlyField()
    refund_policy_text = serializers.ReadOnlyField()
    # We use a method here to call the calculation function from your model
    refund_amount = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'passenger_name', 'passenger_email', 'passenger_phone', 
            'seat_number', 'total_price', 'booking_location', 'status', 
            'flight_departure_datetime', 'flight', 'device_id',
            'flight_origin', 'flight_destination', 'flight_airline',
            'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature',
            'can_cancel', 'refund_policy_text', 'refund_amount' # Added new fields
        ]
        
        extra_kwargs = {
            'status': {'required': False}, 
            'razorpay_order_id': {'required': False, 'allow_null': True},
            'razorpay_payment_id': {'required': False, 'allow_null': True},
            'razorpay_signature': {'required': False, 'allow_null': True},
            'flight': {'required': True},
        }

    def get_refund_amount(self, obj):
        """
        This method calls the calculate_refund_amount() method 
        we added to your Booking model in the previous step.
        """
        # We return it as a string so it is JSON-serializable (avoids Decimal error)
        return str(obj.calculate_refund_amount())

class FoodOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodOrder
        fields = '__all__'