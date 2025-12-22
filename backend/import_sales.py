import json
import psycopg2
import os

# 1. Database Configuration
# Using the standard Docker credentials for MarkSolution
DB_CONFIG = {
    "host": "localhost", # Running from host machine (or 'db' if inside docker)
    "database": "marksolution",
    "user": "markuser",
    "password": "markpass",
    "port": "5432"
}

def import_sales_data(json_file_path):
    print(f"🚀 Starting import from {json_file_path}...")
    
    try:
        # 1. Read JSON Data
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            
        if not isinstance(data, list):
            print("❌ Error: JSON root must be a list of records.")
            return

        print(f"📄 Found {len(data)} records to process.")
        
        # 2. Connect to Database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        inserted_count = 0
        skipped_count = 0
        
        # 3. Process Records
        for record in data:
            # Flexible Parsing: Handle various key names just in case
            sale_date = record.get("date") or record.get("period")
            total_sales = record.get("total_sales") or record.get("total_sale") # Handle typo
            
            if not sale_date or total_sales is None:
                print(f"⚠️ Skipping invalid record: {record}")
                continue
                
            # 4. Duplicate Check (Prevent overwriting)
            cur.execute("SELECT 1 FROM sales WHERE sale_date = %s", (sale_date,))
            exists = cur.fetchone()
            
            if exists:
                skipped_count += 1
                # print(f"⏭️  Skipping existing date: {sale_date}")
            else:
                # 5. Insert New Record
                # item_name is "Imported_Sales" to distinguish source
                cur.execute(
                    "INSERT INTO sales (item_name, amount, sale_date) VALUES (%s, %s, %s)",
                    ("Imported_Sale", total_sales, sale_date)
                )
                inserted_count += 1
                
        # 6. Commit Transaction
        conn.commit()
        
        print("-" * 30)
        print("✅ IMPORT COMPLETE")
        print(f"📥 Inserted: {inserted_count}")
        print(f"⏭️  Skipped:  {skipped_count}")
        print("-" * 30)
        
        cur.close()
        conn.close()

    except FileNotFoundError:
        print(f"❌ File not found: {json_file_path}")
    except psycopg2.OperationalError:
        print("❌ Could not connect to database. Is it running?")
        print("Try running: docker-compose up db -d")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    # Example usage: python3 import_sales.py
    # Ensure sales_2025.json is in the same folder
    import_sales_data("sales_2025.json")
