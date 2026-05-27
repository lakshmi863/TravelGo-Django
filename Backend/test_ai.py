import requests

# MAKE SURE THIS URL MATCHES YOUR urls.py (api/chat/)
URL = "http://127.0.0.1:8000/api/chat/" 

def test_chat(user_message):
    print(f"\n--- User: {user_message} ---")
    try:
        response = requests.post(URL, json={"message": user_message})
        
        # DEBUG: Print the status code and raw text if it's not 200
        if response.status_code != 200:
            print(f"❌ Server Error ({response.status_code})")
            print(f"DEBUG INFO: {response.text[:200]}") # Print the first 200 chars of the HTML error
            return

        data = response.json()
        print(f"AI Reply: {data.get('reply')}")
        if data.get('data_type') == 'flight_list':
            print("🚀 [SUCCESS] Flight cards found!")
            for f in data.get('data', []):
                print(f"   - {f['airline']} | {f['origin']} -> {f['destination']} | ₹{f['price']}")

    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_chat("Hi, how are you?")
    test_chat("I want to fly from Mumbai to Delhi")