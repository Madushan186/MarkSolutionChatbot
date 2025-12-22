import psycopg2
from datetime import date, timedelta

# DB Config
DB_CONFIG = {
    "host": "localhost",
    "database": "marksolution",
    "user": "markuser",
    "password": "markpass",
    "port": "5432"
}

def check_coverage(year=2025):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        # Count distinct days with sales
        # We assume 'sales' text table logic: check distinct sale_date
        query = "SELECT COUNT(DISTINCT sale_date) FROM sales WHERE sale_date >= %s AND sale_date <= %s"
        cur.execute(query, (start_date, end_date))
        count = cur.fetchone()[0]
        
        # Get min and max dates found
        query_range = "SELECT MIN(sale_date), MAX(sale_date) FROM sales WHERE sale_date >= %s AND sale_date <= %s"
        cur.execute(query_range, (start_date, end_date))
        min_date, max_date = cur.fetchone()

        cur.close()
        conn.close()
        
        print(f"--- 2025 Data Coverage Report ---")
        print(f"Total Days with Data: {count}")
        print(f"Earliest Date: {min_date}")
        print(f"Latest Date: {max_date}")
        
        # Expected days up to today (Dec 22)
        today = date(2025, 12, 22) # Hardcoded based on prompt context 'current local time: 2025-12-22'
        days_passed = (today - start_date).days + 1
        
        print(f"Expected Days (Up to Dec 22): {days_passed}")
        
        if count >= 350: # Roughly full year
             print("✅ Conclusion: YES, we have data for nearly the entire year.")
        elif count >= days_passed - 5: # Allow small margin
             print("✅ Conclusion: YES, we have data up to today.")
        else:
             print(f"⚠️ Conclusion: NO, we are missing data. Have {count} days, expected approx {days_passed}.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_coverage(2025)
