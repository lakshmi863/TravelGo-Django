# flights/serializers.py
from rest_framework import serializers
from .models import Flight, Booking, FoodOrder

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    flight_origin = serializers.ReadOnlyField(source='flight.origin')
    flight_destination = serializers.ReadOnlyField(source='flight.destination')
    flight_airline = serializers.ReadOnlyField(source='flight.airline')

    class Meta:
        model = Booking
        fields = [
            'id', 'passenger_name', 'passenger_email', 'passenger_phone', 
            'seat_number', 'total_price', 'booking_location', 'status', 
            'flight_departure_datetime', 'flight', 'device_id',
            'flight_origin', 'flight_destination', 'flight_airline',
            'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature' 
        ]
        
        # SQUARING FIX: These fields shouldn't stop the POST request 
        # because they are filled by the BACKEND logic later.
        extra_kwargs = {
            'status': {'required': False}, 
            'razorpay_order_id': {'required': False, 'allow_null': True},
            'razorpay_payment_id': {'required': False, 'allow_null': True},
            'razorpay_signature': {'required': False, 'allow_null': True},
            # VERY IMPORTANT: If your flight FK is failing
            'flight': {'required': True},
        }

class FoodOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodOrder
        fields = '__all__'