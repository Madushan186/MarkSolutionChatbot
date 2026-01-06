import accounting
import sqlite3
import os

# Ensure we use the right DB
# If running from backend dir, it's local.
print("Testing Accounting Hierarchy Logic...")

# 1. Test Hierarchy Tree
print("\n--- Testing Hierarchy Tree ---")
tree = accounting.get_hierarchy_tree()
for row in tree:
    print(row)

# Expect: Assets (1) -> Current Assets (2) -> Cash/Bank (3)
#         Income (1) -> Operating Revenue (2) -> Sales Revenue (3)

# 2. Test Aggregation (Sales Revenue)
# We know Sales Revenue has data from migration.
print("\n--- Testing Sales Revenue (Leaf) ---")
rev_bal, msg = accounting.get_account_balance("Sales Revenue", 2025)
print(f"Sales Revenue 2025: {rev_bal} ({msg})")
# Should be > 0

# 3. Test Aggregation (Operating Revenue - Group)
print("\n--- Testing Operating Revenue (Group) ---")
op_bal, msg = accounting.get_account_balance("Operating Revenue", 2025)
print(f"Operating Revenue 2025: {op_bal} ({msg})")

# 4. Test Aggregation (Income - Root)
print("\n--- Testing Income (Root) ---")
inc_bal, msg = accounting.get_account_balance("Income", 2025)
print(f"Income 2025: {inc_bal} ({msg})")

# Assert Tree Logic
if rev_bal == op_bal == inc_bal and rev_bal > 0:
    print("✅ SUCCESS: Hierarchy Aggregation works (Leaf == Parent == Root for this simple tree)")
else:
    print("❌ FAILURE: Aggregation mismatch.")

# 5. Test Assets (Should be 0 as we added no data)
print("\n--- Testing Assets balance ---")
asset_bal, msg = accounting.get_account_balance("Assets", 2025)
print(f"Assets 2025: {asset_bal} ({msg})")
