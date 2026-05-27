import os
import uuid 
import json
import openai
from django.conf import settings
from django.db import transaction
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action 
from rest_framework.views import APIView

from django.core.cache import cache

from .models import Flight, Booking, FoodOrder
from .serializers import FlightSerializer, BookingSerializer, FoodOrderSerializer

# Initialize OpenRouter Client
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
)
print(f"DEBUG: My API Key is: {settings.OPENROUTER_API_KEY}")
# ==============================================================================
# 1. FLIGHT VIEWSET (Searchable)
# ==============================================================================
class FlightViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Flights. 
    Enhanced with search filtering for Origin, Destination, and Airline.
    """
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def list(self, request, *args, **kwargs):
        # 1. Create a unique key based on the URL parameters (e.g., origin=Mumbai&destination=Delhi)
        params = request.query_params.urlencode()
        cache_key = f"flights_list_{params}"

        # 2. TRY to get the data from Redis/Cache first
        cached_data = cache.get(cache_key)

        # 3. If the data is in the cache, return it immediately (Fast!)
        if cached_data is not None:
            return Response(cached_data)

        # 4. If NOT in cache, perform the actual Database Query
        response = super().list(request, *args, **kwargs)
        
        # 5. Save the results into the cache so the NEXT user gets it instantly
        # We store 'response.data' (the actual list of flights)
        cache.set(cache_key, response.data, 300) # Cache for 300 seconds (5 mins)
        
        return response

    def get_queryset(self):
        """
        Allows users to search via API: 
        /api/flights/?origin=Mumbai
        /api/flights/?destination=Delhi
        """
        queryset = Flight.objects.all().order_by('price') # Default sort by cheapest
        origin = self.request.query_params.get('origin')
        destination = self.request.query_params.get('destination')
        airline = self.request.query_params.get('airline')

        if origin:
            queryset = queryset.filter(origin__icontains=origin)
        if destination:
            queryset = queryset.filter(destination__icontains=destination)
        if airline:
            queryset = queryset.filter(airline__icontains=airline)
            
        return queryset


# ==============================================================================
# 2. BOOKING VIEWSET (Booking, Squaring, Cancellation, Refunds)
# ==============================================================================
class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Bookings. 
    Handles instant squaring, refund calculations, and cancellation.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_queryset(self):
        """Used by the MyBookings section to filter by passenger email."""
        queryset = Booking.objects.all().order_by('-created_at')
        email = self.request.query_params.get('email', None)
        if email is not None:
            queryset = queryset.filter(passenger_email=email)
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Instant Storage Logic:
        Creates a 'BOOKED' record immediately so it shows in 'My Bookings'.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 1. Generate unique local squaring IDs
        local_order_id = f"ORD_LOC_{uuid.uuid4().hex[:10].upper()}"
        local_payment_id = f"PAY_LOC_{uuid.uuid4().hex[:12].upper()}"

        try:
            with transaction.atomic():
                booking = serializer.save(
                    status='BOOKED', 
                    razorpay_order_id=local_order_id,
                    razorpay_payment_id=local_payment_id,
                    razorpay_signature="SQUARED_ON_CLOUD"
                )

                # 2. Attempt to send confirmation email
                try:
                    self.send_booking_confirmation(booking)
                except Exception as email_err:
                    print(f"📧 EMAIL LOG ERROR (Non-fatal): {email_err}")

            return Response({
                "message": "Booking Stored and Squared!",
                "booking_id": booking.id,
                "mock_order_id": local_order_id,
                "transaction_id": local_payment_id,
                "amount": booking.total_price,
                "passenger_name": booking.passenger_name,
                "status": "BOOKED"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Database storage failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def verify_payment(self, request, pk=None):
        booking = self.get_object()
        return Response({"message": "Data already squared", "transaction_id": booking.razorpay_payment_id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel_ticket(self, request, pk=None):
        """
        Full Cancellation & Refund Logic.
        Uses model properties to calculate exact refund amount.
        """
        booking = self.get_object()

        # 1. Check Hard Rule (4-hour departure window)
        if not booking.can_cancel:
            return Response(
                {"message": "Cancellation window closed. Flight is too close to departure."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Check if already cancelled
        if booking.status == 'CANCELLED':
            return Response(
                {"message": "This ticket is already cancelled."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # 3. Perform calculations using Model logic
                refund_amount = booking.calculate_refund_amount()
                refund_text = booking.refund_policy_text

                # 4. Update record
                booking.status = 'CANCELLED'
                booking.save()

                # 5. Prepare email context
                context = {
                    'passenger_name': booking.passenger_name,
                    'airline': booking.flight.airline,
                    'refund_status': refund_text,
                    'refund_amount': f"₹{refund_amount}",
                    'origin': booking.flight.origin,
                    'destination': booking.flight.destination,
                    'seat_number': booking.seat_number
                }

                # 6. Send cancellation email
                try:
                    self.send_professional_email(
                        'Booking Cancelled & Refund Processed', 
                        context, 
                        'emails/cancellation_email.html', 
                        booking.passenger_email
                    )
                except Exception as e:
                    print(f"⚠️ Cancellation email failed: {e}")

            # 7. Return Success Response
            return Response({
                "message": "Successfully Cancelled.",
                "status": "CANCELLED",
                "refund_amount": str(refund_amount),
                "refund_policy": refund_text
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Cancellation process failed: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    # --- Email Helpers ---

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
        """Handles branded HTML emails with logo attachments."""
        try:
            html_content = render_to_string(template, context)
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email='lalit.lakshmipathi@gmail.com',
                to=[recipient_email],
            )
            email.attach_alternative(html_content, "text/html")

            logo_path = os.path.join(settings.BASE_DIR, 'flights', 'TravelGo_logo.png')
            if os.path.exists(logo_path):
                try:
                    with open(logo_path, 'rb') as f:
                        logo = MIMEImage(f.read())
                        logo.add_header('Content-ID', '<logo_image>')
                        logo.add_header('Content-Disposition', 'inline', filename='TravelGo_logo.png')
                        email.attach(logo)
                except Exception:
                    print("⚠️ Attachment failed - continuing without logo.")

            email.send(fail_silently=False)
            print(f"✅ Success! Email sent to {recipient_email}")

        except Exception as fatal_e:
            print(f"❌ SMTP Fatal Error: {fatal_e}")


# ==============================================================================
# 3. FOOD ORDER VIEWSET
# ==============================================================================
class FoodOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Food Orders."""
    queryset = FoodOrder.objects.all()
    serializer_class = FoodOrderSerializer


# ==============================================================================
# 4. AI CHAT VIEW (OpenRouter + Function Calling)
# ==============================================================================
class AIChatView(APIView):
    """
    AI Agent that can query the database using 'Function Calling'.
    If a user asks for flights, the AI calls 'get_flights' to get real data.
    """
    def post(self, request):
        user_message = request.data.get("message")
        if not user_message:
            return Response({"error": "No message provided"}, status=400)

        try:
            # 1. Define the Tools available to the AI
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_flights",
                        "description": "Search for available flights in the TravelGo database.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "origin": {"type": "string", "description": "The departure city (e.g. Mumbai)"},
                                "destination": {"type": "string", "description": "The arrival city (e.g. Delhi)"},
                            },
                            "required": ["origin", "destination"],
                        },
                    },
                }
            ]

            messages = [{"role": "user", "content": user_message}]

            # 2. Ask the AI if it needs a tool
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo", 
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # 3. If AI calls the flight tool, query the actual database
            if tool_calls:
                for tool_call in tool_calls:
                    if tool_call.function.name == "get_flights":
                        args = json.loads(tool_call.function.arguments)
                        
                        # Perform the actual DB search
                        flights = Flight.objects.filter(
                            origin__icontains=args['origin'],
                            destination__icontains=args['destination']
                        )[:5]

                        flight_results = [
                            {
                                "id": f.id,
                                "airline": f.airline,
                                "origin": f.origin,
                                "destination": f.destination,
                                "price": str(f.price)
                            } for f in flights
                        ]

                        # 4. Feed the DB data back to the AI for a natural response
                        messages.append(response_message)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": "get_flights",
                            "content": json.dumps(flight_results),
                        })

                        final_response = client.chat.completions.create(
                            model="openai/gpt-3.5-turbo",
                            messages=messages,
                        )

                        final_text = final_response.choices[0].message.content

                        # 5. Return text AND structured data for React rendering
                        return Response({
                            "reply": final_text,
                            "data_type": "flight_list",
                            "data": flight_results
                        }, status=status.HTTP_200_OK)

            # If it's just a regular conversation
            return Response({
                "reply": response_message.content,
                "data_type": "text",
                "data": []
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=500)