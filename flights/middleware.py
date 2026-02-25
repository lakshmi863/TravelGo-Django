# flights/middleware.py
import json
import re
from django.http import JsonResponse

class BookingValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # We only validate POST requests going to our bookings endpoint
        if request.path == '/api/bookings/' and request.method == 'POST':
            try:
                # Load the JSON body
                body = json.loads(request.body)
                
                # 1. Validate Name
                name = body.get('passenger_name', '')
                if not name or len(name) < 3:
                    return JsonResponse({"message": "Middleware Error: Name must be at least 3 characters."}, status=400)

                # 2. Validate Email
                email = body.get('passenger_email', '')
                email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                if not re.match(email_regex, email):
                    return JsonResponse({"message": "Middleware Error: Invalid email format."}, status=400)

                # 3. Validate Phone (numeric and at least 10 digits)
                phone = body.get('passenger_phone', '')
                if not str(phone).isdigit() or len(str(phone)) < 10:
                    return JsonResponse({"message": "Middleware Error: Phone must be at least 10 digits."}, status=400)

                # 4. Validate Seat Format (e.g., 1A, 10F)
                seat = body.get('seat_number', '')
                if not re.match(r'^\d+[A-F]$', seat):
                    return JsonResponse({"message": "Middleware Error: Seat must be format like '5A' or '10C'."}, status=400)

            except json.JSONDecodeError:
                return JsonResponse({"message": "Middleware Error: Malformed JSON data."}, status=400)

        # If data is valid, proceed to the view
        return self.get_response(request)