import requests
import psycopg2
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Config
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "marksolution")
DB_USER = os.getenv("POSTGRES_USER", "markuser")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "markpass")

API_URL = "https://api.emark.live/api/mobile/sales"
HEADERS = {"X-Forwarded-For": "144.76.94.137"}

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        print(f"❌ DB Connection Failed: {e}")
        return None

def fetch_branch_data(br_id):
    payload = {
        "db": "84",
        "br_id": str(br_id),
        "year": "2025",
        "type": "daily",
        "range": "365"
    }
    
    try:
        res = requests.post(API_URL, headers=HEADERS, data=payload, timeout=30)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"⚠️ API Error for Branch {br_id}: {e}")
        return None

def sync_branch(br_id):
    print(f"🔄 Syncing Branch {br_id}...")
    
    data = fetch_branch_data(br_id)
    if not data or "data" not in data:
        print(f"   ⚠️ No data found for Branch {br_id}")
        return

    conn = get_db_connection()
    if not conn:
        return

    cur = conn.cursor()
    
    # 1. Delete existing 2025 data for this branch to avoid dupes
    cur.execute("DELETE FROM sales WHERE EXTRACT(YEAR FROM sale_date) = 2025 AND br_id = %s", (br_id,))
    
    # 2. Insert new data
    count = 0
    for row in data["data"]:
        # row: {"period": "2025-01-01", "total_sale": 123.45}
        period = row.get("period")
        amount = float(row.get("total_sales", row.get("total_sale", 0)))
        
        if period:
            # For daily API, period is YYYY-MM-DD
            date_str = period
            
            # Insert
            cur.execute("""
                INSERT INTO sales (sale_date, amount, br_id, item_name)
                VALUES (%s, %s, %s, %s)
            """, (date_str, amount, br_id, f"Daily_Sales_{date_str}"))
            count += 1
            
    conn.commit()
    cur.close()
    conn.close()
    print(f"   ✅ Branch {br_id}: Synced {count} daily records.")

if __name__ == "__main__":
    print("🚀 Starting Full Sync (Branches 1-10)...")
    for i in range(1, 11):
        sync_branch(i)
    print("🏁 Sync Complete.")
