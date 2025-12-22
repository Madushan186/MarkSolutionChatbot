import requests
import psycopg2
from datetime import date, timedelta
import time

# --- CONFIGURATION ---
DB_CONFIG = {
    "host": "localhost",
    "database": "marksolution",
    "user": "markuser",
    "password": "markpass"
}

API_URL = "https://api.emark.live/api/mobile/sales"
HEADERS = {"X-Forwarded-For": "144.76.94.137"}

def sync_entire_year(year=2025):
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
    except Exception as e:
        print(f"❌ DB Connection Failed: {e}")
        return

    print(f"🚀 Starting Sync for {year} (Branch 1) - Monthly Mode...")

    # Prepare API Request with User's specific parameters
    payload = {
        'db': '84',
        'br_id': '1',
        'year': str(year),
        'range': '12',
        'type': 'monthly'
    }
    
    try:
        # 1. Fetch from API
        response = requests.post(API_URL, headers=HEADERS, data=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Clear existing Branch 1 data for this year to avoid duplicates/mix
            print("🧹 Clearing old Branch 1 data for 2025...")
            cur.execute("DELETE FROM sales WHERE EXTRACT(YEAR FROM sale_date) = %s AND br_id = 1", (year,))
            
            if "data" in data and isinstance(data.get("data"), list):
                 for row in data["data"]:
                     # period: "2025-01", "2025-02"
                     period = row.get("period")
                     val = float(row.get("total_sales", row.get("total_sale", 0)))
                     
                     if period:
                         # Append "-01" to make it a date
                         sale_date_str = f"{period}-01"
                         # Insert
                         cur.execute(
                            "INSERT INTO sales (item_name, amount, sale_date, br_id) VALUES (%s, %s, %s, %s)",
                            (f"Monthly_Total_{sale_date_str}", val, sale_date_str, 1)
                         )
            
            conn.commit()
            print("✅ Monthly Data Synced Successfully!")
            
        else:
            print(f"❌ API Error: {response.status_code}")

    except Exception as e:
        print(f"❌ Sync Error: {e}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    sync_entire_year(2025)
