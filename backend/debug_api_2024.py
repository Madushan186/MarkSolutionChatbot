import requests
import json

API_URL = "https://api.emark.live/api/mobile/sales"
HEADERS = {"X-Forwarded-For": "144.76.94.137"}

def check_2024_raw():
    payload = {
        'db': '84',
        'br_id': '1',
        'year': '2024',
        'range': '730', 
        'type': 'daily'
    }
    
    print("Sending Payload:", payload)
    try:
        resp = requests.post(API_URL, headers=HEADERS, data=payload, timeout=20)
        data = resp.json()
        
        rows = data.get("data", [])
        print(f"Received {len(rows)} rows.")
        
        # Analyse Date Range
        dates = [row.get('period') for row in rows if row.get('period')]
        if dates:
            dates.sort()
            print(f"📅 Date Range: {dates[0]} to {dates[-1]}")
            
            june_dates = [d for d in dates if "2024-06" in d]
            print(f"📅 Found {len(june_dates)} records in June 2024.")
        else:
            print("⚠️ No dates found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_2024_raw()
