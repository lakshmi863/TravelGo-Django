from django.core.management.base import BaseCommand
from flights.models import Flight

class Command(BaseCommand):
    help = 'Bulk upload 100 production-ready flights for TravelGo'

    def handle(self, *args, **kwargs):
        self.stdout.write("🧹 Wiping database for a clean square...")
        Flight.objects.all().delete()

        # Define 100 diverse flights
        flight_data = [
            # MUMBAI HUB
            {"airline": "IndiGo", "origin": "Mumbai", "destination": "Delhi", "price": 4200},
            {"airline": "Air India", "origin": "Mumbai", "destination": "Bangalore", "price": 3800},
            {"airline": "Akasa Air", "origin": "Mumbai", "destination": "Hyderabad", "price": 3100},
            {"airline": "SpiceJet", "origin": "Mumbai", "destination": "Goa", "price": 2800},
            {"airline": "Air India Express", "origin": "Mumbai", "destination": "Kochi", "price": 4500},
            {"airline": "IndiGo", "origin": "Mumbai", "destination": "Chennai", "price": 4100},
            {"airline": "Akasa Air", "origin": "Mumbai", "destination": "Kolkata", "price": 5200},
            {"airline": "Air India", "origin": "Mumbai", "destination": "Dubai", "price": 14500},
            {"airline": "IndiGo", "origin": "Mumbai", "destination": "Singapore", "price": 18200},
            {"airline": "Air India", "origin": "Mumbai", "destination": "London", "price": 48000},

            # DELHI HUB
            {"airline": "IndiGo", "origin": "Delhi", "destination": "Mumbai", "price": 4400},
            {"airline": "Air India", "origin": "Delhi", "destination": "Bangalore", "price": 5500},
            {"airline": "SpiceJet", "origin": "Delhi", "destination": "Jaipur", "price": 2200},
            {"airline": "IndiGo", "origin": "Delhi", "destination": "Leh", "price": 7800},
            {"airline": "Akasa Air", "origin": "Delhi", "destination": "Hyderabad", "price": 4900},
            {"airline": "Air India Express", "origin": "Delhi", "destination": "Dubai", "price": 12800},
            {"airline": "Air India", "origin": "Delhi", "destination": "New York", "price": 75000},
            {"airline": "SpiceJet", "origin": "Delhi", "destination": "Kathmandu", "price": 8500},
            {"airline": "IndiGo", "origin": "Delhi", "destination": "Pune", "price": 5100},
            {"airline": "Akasa Air", "origin": "Delhi", "destination": "Ahmedabad", "price": 3200},

            # BANGALORE HUB
            {"airline": "Akasa Air", "origin": "Bangalore", "destination": "Mumbai", "price": 3600},
            {"airline": "IndiGo", "origin": "Bangalore", "destination": "Delhi", "price": 5400},
            {"airline": "Air India", "origin": "Bangalore", "destination": "Hyderabad", "price": 2800},
            {"airline": "IndiGo", "origin": "Bangalore", "destination": "Chennai", "price": 2100},
            {"airline": "SpiceJet", "origin": "Bangalore", "destination": "Kolkata", "price": 6200},
            {"airline": "Air India Express", "origin": "Bangalore", "destination": "Goa", "price": 3300},
            {"airline": "IndiGo", "origin": "Bangalore", "destination": "Lucknow", "price": 5100},
            {"airline": "Air India", "origin": "Bangalore", "destination": "Paris", "price": 52000},
            {"airline": "Akasa Air", "origin": "Bangalore", "destination": "Pune", "price": 3100},
            {"airline": "IndiGo", "origin": "Bangalore", "destination": "Amritsar", "price": 7200},

            # HYDERABAD HUB
            {"airline": "IndiGo", "origin": "Hyderabad", "destination": "Visakhapatnam", "price": 2500},
            {"airline": "SpiceJet", "origin": "Hyderabad", "destination": "Tirupati", "price": 2200},
            {"airline": "Air India", "origin": "Hyderabad", "destination": "Delhi", "price": 5100},
            {"airline": "Akasa Air", "origin": "Hyderabad", "destination": "Bangalore", "price": 2900},
            {"airline": "Air India Express", "origin": "Hyderabad", "destination": "Mumbai", "price": 3200},
            {"airline": "IndiGo", "origin": "Hyderabad", "destination": "Chennai", "price": 2700},
            {"airline": "Air India", "origin": "Hyderabad", "destination": "London", "price": 55000},
            {"airline": "IndiGo", "origin": "Hyderabad", "destination": "Goa", "price": 3400},
            {"airline": "Akasa Air", "origin": "Hyderabad", "destination": "Kolkata", "price": 5800},
            {"airline": "IndiGo", "origin": "Hyderabad", "destination": "Raipur", "price": 3100},

            # CHENNAI & KOLKATA TIERS
            {"airline": "IndiGo", "origin": "Chennai", "destination": "Coimbatore", "price": 2400},
            {"airline": "Air India", "origin": "Chennai", "destination": "Port Blair", "price": 8500},
            {"airline": "SpiceJet", "origin": "Kolkata", "destination": "Guwahati", "price": 2800},
            {"airline": "IndiGo", "origin": "Kolkata", "destination": "Bagdogra", "price": 3100},
            {"airline": "Air India", "origin": "Kolkata", "destination": "Bangkok", "price": 14200},
            {"airline": "Air India Express", "origin": "Chennai", "destination": "Colombo", "price": 9500},
            {"airline": "Akasa Air", "origin": "Kolkata", "destination": "Bhubaneswar", "price": 2200},
            {"airline": "IndiGo", "origin": "Kolkata", "destination": "Ranchi", "price": 2600},
            {"airline": "Air India", "origin": "Chennai", "destination": "Madurai", "price": 2900},
            {"airline": "SpiceJet", "origin": "Kolkata", "destination": "Delhi", "price": 5800},

            # TIER 2 & HOLIDAY ROUTES
            {"airline": "IndiGo", "origin": "Goa", "destination": "Mumbai", "price": 2900},
            {"airline": "SpiceJet", "origin": "Goa", "destination": "Delhi", "price": 5200},
            {"airline": "Akasa Air", "origin": "Kochi", "destination": "Bangalore", "price": 2400},
            {"airline": "Air India", "origin": "Ahmedabad", "destination": "Mumbai", "price": 2800},
            {"airline": "IndiGo", "origin": "Pune", "destination": "Nagpur", "price": 3400},
            {"airline": "SpiceJet", "origin": "Jaipur", "destination": "Jaisalmer", "price": 1800},
            {"airline": "Air India Express", "origin": "Lucknow", "destination": "Dubai", "price": 11500},
            {"airline": "IndiGo", "origin": "Surat", "destination": "Delhi", "price": 4200},
            {"airline": "Akasa Air", "origin": "Varanasi", "destination": "Mumbai", "price": 5100},
            {"airline": "Air India", "origin": "Indore", "destination": "Hyderabad", "price": 3700},

            # INTERNATIONAL SEGMENT
            {"airline": "Air India", "origin": "Dubai", "destination": "Delhi", "price": 12400},
            {"airline": "IndiGo", "origin": "Singapore", "destination": "Chennai", "price": 13500},
            {"airline": "Air India", "origin": "London", "destination": "Mumbai", "price": 51000},
            {"airline": "Air India Express", "origin": "Abu Dhabi", "destination": "Kochi", "price": 10800},
            {"airline": "SpiceJet", "origin": "Dubai", "destination": "Mumbai", "price": 11200},
            {"airline": "IndiGo", "origin": "Bangkok", "destination": "Kolkata", "price": 12800},
            {"airline": "Air India", "origin": "San Francisco", "destination": "Delhi", "price": 82000},
            {"airline": "IndiGo", "origin": "Doha", "destination": "Hyderabad", "price": 15500},
            {"airline": "Air India Express", "origin": "Muscat", "destination": "Calicut", "price": 9800},
            {"airline": "IndiGo", "origin": "Hong Kong", "destination": "Delhi", "price": 22000},

            # MIXED UTILITY ROUTES (20+ more)
            {"airline": "IndiGo", "origin": "Mangalore", "destination": "Mumbai", "price": 3200},
            {"airline": "Akasa Air", "origin": "Guwahati", "destination": "Bangalore", "price": 7200},
            {"airline": "Air India", "origin": "Delhi", "destination": "Dehradun", "price": 2800},
            {"airline": "SpiceJet", "origin": "Mumbai", "destination": "Aurangabad", "price": 2100},
            {"airline": "IndiGo", "origin": "Bhopal", "destination": "Hyderabad", "price": 3500},
            {"airline": "Akasa Air", "origin": "Mumbai", "destination": "Varanasi", "price": 4800},
            {"airline": "Air India Express", "origin": "Surat", "destination": "Bangalore", "price": 4100},
            {"airline": "IndiGo", "origin": "Delhi", "destination": "Patna", "price": 4200},
            {"airline": "Air India", "origin": "Vijayawada", "destination": "Hyderabad", "price": 1900},
            {"airline": "SpiceJet", "origin": "Delhi", "destination": "Srinagar", "price": 4800},
            {"airline": "IndiGo", "origin": "Udaipur", "destination": "Mumbai", "price": 3100},
            {"airline": "Akasa Air", "origin": "Mumbai", "destination": "Ahmedabad", "price": 2600},
            {"airline": "Air India", "origin": "Pune", "destination": "Bangalore", "price": 3900},
            {"airline": "IndiGo", "origin": "Jodhpur", "destination": "Delhi", "price": 3500},
            {"airline": "SpiceJet", "origin": "Patna", "destination": "Mumbai", "price": 5200},
            {"airline": "Air India Express", "origin": "Mumbai", "destination": "Mangalore", "price": 2800},
            {"airline": "IndiGo", "origin": "Shimla", "destination": "Delhi", "price": 4500},
            {"airline": "Akasa Air", "origin": "Guwahati", "destination": "Delhi", "price": 6100},
            {"airline": "Air India", "origin": "Rajkot", "destination": "Mumbai", "price": 3200},
            {"airline": "IndiGo", "origin": "Chennai", "destination": "Port Blair", "price": 9200},
            {"airline": "SpiceJet", "origin": "Delhi", "destination": "Kolkata", "price": 6100},
            {"airline": "Air India", "origin": "Trivandrum", "destination": "Delhi", "price": 6800},
            {"airline": "Akasa Air", "origin": "Hyderabad", "destination": "Kochi", "price": 2900},
            {"airline": "IndiGo", "origin": "Mumbai", "destination": "Lucknow", "price": 4900},
            {"airline": "IndiGo", "origin": "Mumbai", "destination": "Amritsar", "price": 5400},
            {"airline": "SpiceJet", "origin": "Varanasi", "destination": "Delhi", "price": 4100},
            {"airline": "Akasa Air", "origin": "Bangalore", "destination": "Agartala", "price": 6800},
            {"airline": "IndiGo", "origin": "Guwahati", "destination": "Delhi", "price": 5100},
            {"airline": "Air India Express", "origin": "Calicut", "destination": "Riyadh", "price": 14200},
            {"airline": "Air India", "origin": "Sydney", "destination": "Delhi", "price": 72000},
        ]

        # Bulk creation
        for f in flight_data:
            Flight.objects.create(
                airline=f["airline"],
                origin=f["origin"],
                destination=f["destination"],
                price=f["price"],
                special_offer="Official Flight Square"
            )

        self.stdout.write(self.style.SUCCESS(f"🚀 Successfully Uploaded {len(flight_data)} Flights! TravelGo is now Squared."))