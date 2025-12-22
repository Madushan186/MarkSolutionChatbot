import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "marksolution",
    "user": "markuser",
    "password": "markpass",
    "port": "5432"
}

def check_jan_sales():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("--- January 2025 Sales ---")
        cur.execute("SELECT sale_date, amount, br_id FROM sales WHERE sale_date >= '2025-01-01' AND sale_date <= '2025-01-31' ORDER BY sale_date;")
        rows = cur.fetchall()
        
        total = 0
        for r in rows:
            print(f"{r[0]} | {r[1]} | br_id={r[2]}")
            total += r[1]
            
        print(f"Total: {total:,.2f}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_jan_sales()
