import requests
import sqlite3
from datetime import date, timedelta
import time
import os

# --- CONFIGURATION ---
DB_NAME = "sales.db"

API_URL = "https://api.emark.live/api/mobile/sales"
HEADERS = {"X-Forwarded-For": "144.76.94.137"}

def init_db(cur):
    """Ensure the sales table exists with the correct schema."""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            sale_date TEXT NOT NULL,
            amount REAL NOT NULL,
            br_id INTEGER DEFAULT 1
        )
    """)

def sync_entire_year(year=2025):
    # Connect to SQLite
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        init_db(cur)
    except Exception as e:
        print(f"❌ DB Connection Failed: {e}")
        return

    # Sync Branches 1 to 5
    branches = [1, 2, 3, 4, 5]
    
    print(f"🚀 Starting Sync for {year} (Branches: {branches})...")

    total_records = 0
    
    for br_id in branches:
        print(f"   Now Processing Branch {br_id}...")
        
        # Prepare API Request
        payload = {
            'db': '84',
            'br_id': str(br_id),
            'year': str(year),
            'range': '365', 
            'type': 'daily'
        }
        
        try:
            # 1. Fetch from API
            response = requests.post(API_URL, headers=HEADERS, data=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Clear existing data for this branch/year
                cur.execute("DELETE FROM sales WHERE strftime('%Y', sale_date) = ? AND br_id = ?", (str(year), br_id))
                
                count = 0
                if "data" in data and isinstance(data.get("data"), list):
                     for row in data["data"]:
                         # period: "2025-01-01"
                         period = row.get("period")
                         val = float(row.get("total_sales", row.get("total_sale", 0)))
                         
                         if period:
                             sale_date_str = period
                             # Insert
                             cur.execute(
                                "INSERT INTO sales (item_name, amount, sale_date, br_id) VALUES (?, ?, ?, ?)",
                                (f"Daily_Sales_{sale_date_str}", val, sale_date_str, br_id)
                             )
                             count += 1
                
                print(f"      ✅ Branch {br_id}: {count} records")
                total_records += count
                # Be nice to the API
                time.sleep(0.5) 
                
            else:
                print(f"      ❌ Branch {br_id} API Error: {response.status_code}")

        except Exception as e:
            print(f"      ❌ Branch {br_id} Sync Error: {e}")

    conn.commit()
    print(f"🏁 Sync Complete! Total Records: {total_records}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    sync_entire_year(2024)
    sync_entire_year(2025)
