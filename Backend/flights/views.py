import os
import uuid 
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
        queryset = Booking.objects.all().order_by('-created_at')
        email = self.request.query_params.get('email', None)
        if email is not None:
            queryset = queryset.filter(passenger_email=email)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        local_order_id = f"ORDER_LOC_{uuid.uuid4().hex[:10].upper()}"
        try:
            booking = serializer.save(status='PENDING', razorpay_order_id=local_order_id)
            return Response({
                "booking_id": booking.id,
                "mock_order_id": local_order_id,
                "amount": booking.total_price,
                "passenger_name": booking.passenger_name
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Database failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def verify_payment(self, request, pk=None):
        booking = self.get_object()
        local_payment_id = f"PAY_LOC_{uuid.uuid4().hex[:12].upper()}"
        
        try:
            with transaction.atomic():
                booking.status = 'BOOKED'
                booking.razorpay_payment_id = local_payment_id
                booking.razorpay_signature = "SQUARING_SIGNED_OFF"
                booking.save()

                # Step 3: Trigger Email. 
                # We put it in a sub-try so if SMTP fails, the 200 Success still sends!
                try:
                    self.send_booking_confirmation(booking)
                except Exception as email_err:
                    print(f"📧 SMTP LOG: Email failed but booking kept: {email_err}")

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
            return Response({"message": "Cancellation window closed."}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = 'CANCELLED'
        booking.save()

        context = {
            'passenger_name': booking.passenger_name,
            'airline': booking.flight.airline,
            'refund_status': booking.refund_eligibility,
            'origin': booking.flight.origin,
            'destination': booking.flight.destination,
            'seat_number': booking.seat_number
        }
        try:
            self.send_professional_email('Ticket Cancelled', context, 'emails/cancellation_email.html', booking.passenger_email)
        except:
            pass
        return Response({"message": "Successfully Cancelled."}, status=status.HTTP_200_OK)

    def send_booking_confirmation(self, booking):
        context = {
            'passenger_name': booking.passenger_name,
            'airline': booking.flight.airline,
            'origin': booking.flight.origin,
            'destination': booking.flight.destination,
            'seat_number': booking.seat_number,
            'departure_time': booking.flight_departure_datetime.strftime('%d %b %Y, %H:%M') if booking.flight_departure_datetime else "TBD",
            'location': booking.booking_location,
            'device_id': booking.device_id,
            'transaction_id': booking.razorpay_payment_id 
        }
        self.send_professional_email(f'Official Ticket: {booking.flight.airline}', context, 'emails/booking_confirmation.html', booking.passenger_email)

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

            # Production Safe Logo Path
            logo_path = os.path.join(settings.BASE_DIR, 'flights', 'TravelGo_logo.png')
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    logo = MIMEImage(f.read())
                    logo.add_header('Content-ID', '<logo_image>')
                    logo.add_header('Content-Disposition', 'inline', filename='TravelGo_logo.png')
                    email.attach(logo)
            
            email.send(fail_silently=False)
            print(f"✅ Email Sent to {recipient_email}")
        except Exception as e:
            print(f"📧 SMTP Error (Non-Fatal): {e}")

class FoodOrderViewSet(viewsets.ModelViewSet):
    queryset = FoodOrder.objects.all()
    serializer_class = FoodOrderSerializer