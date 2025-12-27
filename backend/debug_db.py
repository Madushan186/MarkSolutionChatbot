import psycopg2
import os
from dotenv import load_dotenv
import calendar

# Load env manually since we are running as script
load_dotenv()

def get_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            database=os.getenv("POSTGRES_DB", "marksolution"),
            user=os.getenv("POSTGRES_USER", "markuser"),
            password=os.getenv("POSTGRES_PASSWORD", "markpass")
        )
        print("✅ DB Connection Successful")
        return conn
    except Exception as e:
        print(f"❌ DB Connection Failed: {e}")
        return None

def fetch_monthly_sum_from_db(year, month_num, br_id=1):
    conn = get_db()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        _, last_day = calendar.monthrange(year, month_num)
        start_date = f"{year}-{month_num:02d}-01"
        end_date = f"{year}-{month_num:02d}-{last_day}"
        
        print(f"🔍 Querying: {start_date} to {end_date} for Branch {br_id}")
        
        query = "SELECT SUM(amount) FROM sales WHERE sale_date >= %s AND sale_date <= %s AND br_id = %s"
        cur.execute(query, (start_date, end_date, br_id))
        row = cur.fetchone()
        
        cur.close()
        conn.close()
        
        val = float(row[0]) if row and row[0] is not None else 0.0
        print(f"✅ Result: {val}")
        return val
        
    except Exception as e:
        print(f"❌ DB Query Error: {e}")
        return None

if __name__ == "__main__":
    print("--- DEBUGGING MARCH 2025 ---")
    fetch_monthly_sum_from_db(2025, 3, 1)
