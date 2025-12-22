import requests
import json
from datetime import date

def verify_live_sales():
    url = "https://api.emark.live/api/mobile/sales"
    headers = {"X-Forwarded-For": "144.76.94.137"}
    
    # Payload for "Live Sales" (Branch 1, Today)
    payload = {
        "db": "84",
        "br_id": "1",
        "year": str(date.today().year),
        "type": "daily",
        "range": "1"
    }
    
    print(f"📡 Querying Live API with payload: {payload}")
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("👇 RAW API RESPONSE 👇")
            print(json.dumps(data, indent=2))
            
            total = 0.0
            if "data" in data and isinstance(data["data"], list):
                for row in data["data"]:
                    # Print each row's total to see if we are summing multiple things
                    val = float(row.get("total_sales", row.get("total_sale", 0)))
                    print(f"Row Date: {row.get('period')} | Amount: {val}")
                    total += val
            
            print(f"✅ Calculated Total: {total:,.2f}")
        else:
            print(f"❌ API Status: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_live_sales()
