import requests
import json

url = "https://api.emark.live/api/mobile/sales"
headers = {"X-Forwarded-For": "144.76.94.137"}

# Testing range=30 to see if we get a LIST of daily records
payload = {
    "db": "84",
    "year": "2025",
    "type": "daily",
    "range": "30" 
}

try:
    print("Sending request with range=30...")
    response = requests.post(url, headers=headers, data=payload, timeout=10)
    data = response.json()
    
    if "data" in data and isinstance(data['data'], list):
        print(f"Number of items: {len(data['data'])}")
        # Print first 2 items to check if they are distinct days
        for i, item in enumerate(data['data'][:3]):
            print(f"Item {i}:", json.dumps(item, indent=2))
    else:
         print("Data key missing or not list:", data.keys())

except Exception as e:
    print("Error:", e)
