import requests
import json
import datetime

API_URL = "https://api.emark.live/api/mobile/sales"
HEADERS = {"X-Forwarded-For": "144.76.94.137"}

def check_2025_raw():
    payload = {
        'db': '84',
        'br_id': '1',
        'year': '2025',
        'range': '30', 
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
            
            # Check for today
            today = "2025-12-28"
            found = [row for row in rows if row.get('period') == today]
            if found:
                print(f"✅ FOUND TODAY ({today}): {found[0]}")
            else:
                 print(f"❌ TODAY ({today}) NOT FOUND.")
        else:
            print("⚠️ No dates found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_2025_raw()
