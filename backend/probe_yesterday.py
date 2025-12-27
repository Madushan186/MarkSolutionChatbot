from main import get_db

def probe():
    conn = get_db()
    cur = conn.cursor()
    
    print("--- Probing Dec 2025 Data ---")
    cur.execute("SELECT sale_date, amount, br_id FROM sales WHERE sale_date >= '2025-12-20' ORDER BY sale_date DESC")
    rows = cur.fetchall()
    
    if not rows:
        print("❌ No data found for Dec 20-31.")
    else:
        for r in rows:
            print(f"✅ Found: {r}")
            
    conn.close()

if __name__ == "__main__":
    probe()
