import requests
import json

url = "https://api.emark.live/api/mobile/sales"
headers = {"X-Forwarded-For": "144.76.94.137"}
# Try to fetch current month (January 2025)
payload = {
    "db": "84",
    "year": "2025",
    "type": "monthly",
    "range": "1" # Last 1 month? Or current month?
}

try:
    print("Sending request...")
    response = requests.post(url, headers=headers, data=payload, timeout=10)
    data = response.json()
    print("Keys:", data.keys())
    if "data" in data:
        print(f"Data List Type: {type(data['data'])}")
        if isinstance(data['data'], list):
            print(f"Number of items: {len(data['data'])}")
            if len(data['data']) > 0:
                print("First Item:", json.dumps(data['data'][0], indent=2))
        else:
             print("Data:", data['data'])
except Exception as e:
    print("Error:", e)
