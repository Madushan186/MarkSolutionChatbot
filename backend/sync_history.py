import requests
import psycopg2
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

def sync_history():
    print("🚀 Starting Historical Data Sync (Strategy: range=365)...")
    
    # 1. Fetch EVERYTHING (Last 365 Days)
    payload = {
        "db": "84",
        "year": "2025",
        "type": "daily",
        "range": "365"
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, data=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        records = data.get("data", [])
        print(f"📄 Found {len(records)} records.")
        
        if not records:
             print("⚠️ No data found.")
             return

        # 2. Connect to DB
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        count_inserted = 0
        count_updated = 0

        for row in records:
            # Format: '2025-01-10'
            date_str = row.get("period") 
            
            # Format: 12345.67
            amount = float(row.get("total_sales", row.get("total_sale", 0)))

            if not date_str or amount == 0:
                continue

            # UPSERT Logic
            cur.execute("SELECT 1 FROM sales WHERE sale_date = %s", (date_str,))
            exists = cur.fetchone()

            if exists:
                cur.execute("UPDATE sales SET amount = %s WHERE sale_date = %s", (amount, date_str))
                count_updated += 1
            else:
                cur.execute("INSERT INTO sales (item_name, amount, sale_date) VALUES (%s, %s, %s)", 
                            (f"API_Sync_{date_str}", amount, date_str))
                count_inserted += 1

        conn.commit()
        cur.close()
        conn.close()
        
        print("-----------------------------------")
        print(f"✅ Sync Complete")
        print(f"🆕 Inserted: {count_inserted}")
        print(f"🔄 Updated:  {count_updated}")
        print("-----------------------------------")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sync_history()
