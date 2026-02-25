import os
import uuid  # Standard Python library for generating unique IDs
from django.conf import settings
from django.db import transaction
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action 

from .models import Flight, Booking, FoodOrder
from .serializers import FlightSerializer, BookingSerializer, FoodOrderSerializer

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_queryset(self):
        queryset = Booking.objects.all().order_by('-created_at') # Newest first
        email = self.request.query_params.get('email', None)
        
        if email is not None:
            # Only return bookings where passenger_email matches the logged-in user
            queryset = queryset.filter(passenger_email=email)
        
        return queryset

    def create(self, request, *args, **kwargs):
        """Step 1: Create a PENDING booking in our database and generate a Local ID"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 1. Generate a unique Mock Order ID locally
        # This acts as our "intent to pay" ID
        local_order_id = f"ORDER_LOC_{uuid.uuid4().hex[:10].upper()}"

        try:
            # 2. Save the Booking as PENDING
            booking = serializer.save(
                status='PENDING',
                razorpay_order_id=local_order_id
            )

            # 3. Return IDs to React
            # In your React file, use these to trigger your custom UPI simulation
            return Response({
                "booking_id": booking.id,
                "mock_order_id": local_order_id,
                "amount": booking.total_price,
                "passenger_name": booking.passenger_name
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Database storage failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def verify_payment(self, request, pk=None):
        """Step 2: Squaring the record locally (Confirming the data)"""
        booking = self.get_object()
        
        # 1. Generate a unique Mock Payment ID locally
        # This is your proof that data is squared/completed
        local_payment_id = f"PAY_LOC_{uuid.uuid4().hex[:12].upper()}"
        local_signature = "SQUARING_SIGNED_OFF_BY_TRAVELGO"

        try:
            # 2. Ensure data integrity using a transaction
            with transaction.atomic():
                booking.status = 'BOOKED'  # Confirmed in Database
                booking.razorpay_payment_id = local_payment_id
                booking.razorpay_signature = local_signature
                booking.save()

                # 3. Trigger Email only after local confirmation
                self.send_booking_confirmation(booking)

            return Response({
                "message": "Payment verified locally & Squared!",
                "transaction_id": local_payment_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            booking.status = 'FAILED'
            booking.save()
            return Response({"message": f"Local Squaring Failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel_ticket(self, request, pk=None):
        booking = self.get_object()
        if not booking.can_cancel:
            return Response({"message": "Cancellation period over (Less than 4h remaining)."}, status=status.HTTP_400_BAD_REQUEST)

        refund_status = booking.refund_eligibility
        booking.status = 'CANCELLED'
        booking.save()

        context = {
            'passenger_name': booking.passenger_name,
            'airline': booking.flight.airline,
            'refund_status': refund_status,
            'origin': booking.flight.origin,
            'destination': booking.flight.destination,
        }

        self.send_professional_email(
            subject=f'Ticket Cancelled: {booking.flight.airline}',
            context=context,
            template='emails/cancellation_email.html',
            recipient_email=booking.passenger_email
        )
        return Response({"message": "Successfully Cancelled."}, status=status.HTTP_200_OK)

    def send_booking_confirmation(self, booking):
        """Helper for Branded Email with the local Transaction ID"""
        context = {
            'passenger_name': booking.passenger_name,
            'airline': booking.flight.airline,
            'origin': booking.flight.origin,
            'destination': booking.flight.destination,
            'seat_number': booking.seat_number,
            'departure_time': booking.flight_departure_datetime.strftime('%d %b %Y, %H:%M') if booking.flight_departure_datetime else "TBD",
            'location': booking.booking_location,
            'device_id': booking.device_id,
            'transaction_id': booking.razorpay_payment_id # Showing the Squared ID to user
        }
        self.send_professional_email(
            subject=f'Official Ticket: {booking.flight.airline}',
            context=context,
            template='emails/booking_confirmation.html',
            recipient_email=booking.passenger_email
        )

    def send_professional_email(self, subject, context, template, recipient_email):
        try:
            html_content = render_to_string(template, context)
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email='TravelGo Reservations <lalit.lakshmipathi@gmail.com>',
                to=[recipient_email],
            )
            email.attach_alternative(html_content, "text/html")

            logo_path = os.path.join(settings.BASE_DIR, 'flights', 'TravelGo_logo.png')
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    logo_data = f.read()
                    logo = MIMEImage(logo_data)
                    logo.add_header('Content-ID', '<logo_image>')
                    logo.add_header('Content-Disposition', 'inline', filename='TravelGo_logo.png')
                    email.attach(logo)
            email.send()
        except Exception as e:
            print(f"Email Error (Backend): {e}")

class FoodOrderViewSet(viewsets.ModelViewSet):
    queryset = FoodOrder.objects.all()
    serializer_class = FoodOrderSerializer