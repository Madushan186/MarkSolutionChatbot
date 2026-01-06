import sqlite3
import os

DB_NAME = "backend/sales.db"

def migrate_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    print("Migrating Database for Accounting Hierarchy...")
    
    # 1. Create accounts table
    try:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            name TEXT NOT NULL,
            level INTEGER NOT NULL,
            type TEXT CHECK(type IN ('ASSET', 'LIABILITY', 'EQUITY', 'INCOME', 'EXPENSE')) NOT NULL,
            allow_ledger TEXT CHECK(allow_ledger IN ('yes', 'no')) NOT NULL,
            FOREIGN KEY(parent_id) REFERENCES accounts(id)
        )
        ''')
        print("✅ 'accounts' table checked/created.")
    except Exception as e:
        print(f"❌ Error creating accounts table: {e}")

    # 2. Add Default Hierarchy (Simple Standard CoA)
    # Check if empty first
    cur.execute("SELECT COUNT(*) FROM accounts")
    if cur.fetchone()[0] == 0:
        print("Populating default CoA...")
        # Roots
        cur.execute("INSERT INTO accounts (name, level, type, allow_ledger) VALUES ('Assets', 1, 'ASSET', 'no')")
        asset_id = cur.lastrowid
        
        cur.execute("INSERT INTO accounts (name, level, type, allow_ledger) VALUES ('Income', 1, 'INCOME', 'no')")
        income_id = cur.lastrowid
        
        cur.execute("INSERT INTO accounts (name, level, type, allow_ledger) VALUES ('Expenses', 1, 'EXPENSE', 'no')")
        expense_id = cur.lastrowid

        # Children for Assets
        cur.execute("INSERT INTO accounts (parent_id, name, level, type, allow_ledger) VALUES (?, 'Current Assets', 2, 'ASSET', 'no')", (asset_id,))
        curr_asset_id = cur.lastrowid
        
        cur.execute("INSERT INTO accounts (parent_id, name, level, type, allow_ledger) VALUES (?, 'Cash on Hand', 3, 'ASSET', 'yes')", (curr_asset_id,))
        cur.execute("INSERT INTO accounts (parent_id, name, level, type, allow_ledger) VALUES (?, 'Bank Accounts', 3, 'ASSET', 'yes')", (curr_asset_id,))
        
        # Children for Income
        cur.execute("INSERT INTO accounts (parent_id, name, level, type, allow_ledger) VALUES (?, 'Operating Revenue', 2, 'INCOME', 'no')", (income_id,))
        op_rev_id = cur.lastrowid
        
        cur.execute("INSERT INTO accounts (parent_id, name, level, type, allow_ledger) VALUES (?, 'Sales Revenue', 3, 'INCOME', 'yes')", (op_rev_id,))
        sales_rev_id = cur.lastrowid # We will link existing sales here

        print("✅ Default CoA populated.")
    else:
        print("ℹ️ CoA already exists, skipping population.")
        # Retrieve Sales Revenue ID for migration
        cur.execute("SELECT id FROM accounts WHERE name = 'Sales Revenue'")
        row = cur.fetchone()
        sales_rev_id = row[0] if row else None

    # 3. Add account_id to sales table
    # Check if column exists
    cur.execute("PRAGMA table_info(sales)")
    columns = [info[1] for info in cur.fetchall()]
    
    if 'account_id' not in columns:
        print("Adding 'account_id' column to sales table...")
        try:
            cur.execute("ALTER TABLE sales ADD COLUMN account_id INTEGER")
            print("✅ Column added.")
            
            # 4. Migrate existing data
            if sales_rev_id:
                print(f"Linking existing sales to Account ID {sales_rev_id} (Sales Revenue)...")
                cur.execute("UPDATE sales SET account_id = ? WHERE account_id IS NULL", (sales_rev_id,))
                print(f"✅ Updated {cur.rowcount} rows.")
            else:
                print("⚠️ Warning: Could not find 'Sales Revenue' account to link existing data.")
        except Exception as e:
            print(f"❌ Error altering sales table: {e}")
    else:
        print("ℹ️ 'account_id' column already exists in sales table.")

    conn.commit()
    conn.close()
    print("Migration Complete.")

if __name__ == "__main__":
    migrate_db()
