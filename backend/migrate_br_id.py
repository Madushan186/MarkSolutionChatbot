import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "marksolution",
    "user": "markuser",
    "password": "markpass",
    "port": "5432"
}

def migrate_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Check if column exists to avoid error
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='sales' AND column_name='br_id';")
        if not cur.fetchone():
            print("Adding br_id column...")
            cur.execute("ALTER TABLE sales ADD COLUMN br_id INTEGER DEFAULT 1;")
            conn.commit()
            print("✅ br_id column added.")
        else:
            print("ℹ️ br_id column already exists.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Migration Error: {e}")

if __name__ == "__main__":
    migrate_db()
