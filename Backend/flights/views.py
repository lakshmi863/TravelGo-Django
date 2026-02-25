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
        local_payment_id = f"PAY_LOC_{uuid.uuid4().hex[:12].upper()}"

        try:
            with transaction.atomic():
                booking = serializer.save(
                    status='BOOKED', 
                    razorpay_order_id=local_order_id,
                    razorpay_payment_id=local_payment_id,
                    razorpay_signature="INSTANT_SQUARE_COMPLETED"
                )

                try:
                    self.send_booking_confirmation(booking)
                except Exception as email_err:
                    print(f"📧 EMAIL LOG ERROR: {email_err}")

            return Response({
                "message": "Booking Success!",
                "booking_id": booking.id,
                "transaction_id": local_payment_id,
                "amount": booking.total_price,
                "passenger_name": booking.passenger_name,
                "status": booking.status
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def verify_payment(self, request, pk=None):
        booking = self.get_object()
        return Response({"message": "Already Squared", "transaction_id": booking.razorpay_payment_id}, status=status.HTTP_200_OK)

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

            # SAFETY LOGO LOGIC
            logo_path = os.path.join(settings.BASE_DIR, 'flights', 'TravelGo_logo.png')
            if os.path.exists(logo_path):
                try:
                    with open(logo_path, 'rb') as f:
                        logo = MIMEImage(f.read())
                        logo.add_header('Content-ID', '<logo_image>')
                        logo.add_header('Content-Disposition', 'inline', filename='TravelGo_logo.png')
                        email.attach(logo)
                except Exception as logo_err:
                    print(f"⚠️ Attachment failed: {logo_err}")

            # Send is inside the MAIN TRY BLOCK
            email.send(fail_silently=False)
            print(f"✅ Success! Email sent to {recipient_email}")

        except Exception as fatal_e:
            print(f"❌ FATAL EMAIL CRASH PREVENTED: {fatal_e}")

class FoodOrderViewSet(viewsets.ModelViewSet):
    queryset = FoodOrder.objects.all()
    serializer_class = FoodOrderSerializer