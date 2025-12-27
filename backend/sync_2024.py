import requests
import psycopg2
import os

# Configuration
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = "marksolution"
DB_USER = "markuser"
DB_PASS = "markpass"

API_URL = "https://api.emark.live/api/mobile/sales"
HEADERS = {"X-Forwarded-For": "144.76.94.137"}

def sync_2024():
    print("🚀 Starting 2024 Data Sync (Branches 1-10)...")
    
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
    except Exception as e:
        print(f"❌ DB Connection Failed: {e}")
        return

    total_records = 0
    
    # Loop through branches 1 to 10
    for br_id in range(1, 11):
        print(f"Fetching 2024 data for Branch {br_id}...")
        
        payload = {
            'db': '84',
            'br_id': str(br_id),
            'year': '2024',
            'range': '800', # Fetch back to early 2024
            'type': 'daily'
        }
        
        try:
            resp = requests.post(API_URL, headers=HEADERS, data=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                rows = data.get("data", [])
                
                # Clear old 2024 data for this branch to avoid duplicates
                cur.execute("DELETE FROM sales WHERE EXTRACT(YEAR FROM sale_date) = 2024 AND br_id = %s", (br_id,))
                
                inserted = 0
                for row in rows:
                    period = row.get("period") # YYYY-MM-DD
                    val = float(row.get("total_sales", row.get("total_sale", 0)))
                    
                    if period and val > 0:
                        cur.execute(
                            "INSERT INTO sales (item_name, amount, sale_date, br_id) VALUES (%s, %s, %s, %s)",
                            (f"Sync2024_Br{br_id}_{period}", val, period, br_id)
                        )
                        inserted += 1
                
                print(f"✅ Branch {br_id}: Synced {inserted} records.")
                total_records += inserted
                conn.commit()
            else:
                print(f"⚠️ Branch {br_id}: API Error {resp.status_code}")
                
        except Exception as e:
            print(f"❌ Branch {br_id} Error: {e}")

    cur.close()
    conn.close()
    print(f"\n🎉 2024 Sync Complete! Total Records: {total_records}")

if __name__ == "__main__":
    sync_2024()
