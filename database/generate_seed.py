
import random
from datetime import datetime, timedelta

# Configuration
TODAY = datetime.now().date()
SQL_FILE = "database/seed_sales.sql"

sql_statements = [
    "TRUNCATE TABLE sales;",  # Clear existing data for strict testing
    "BEGIN;"
]

# 1. Today's Sales (Critical for 'Daily Income' endpoint)
# Generate 5 transactions for today
print(f"Generating data for today: {TODAY}")
for _ in range(5):
    amount = random.randint(2000, 5000)
    sql_statements.append(f"INSERT INTO sales (sale_date, amount) VALUES ('{TODAY}', {amount});")

# 2. Last 7 Days (for trend analysis potential)
for i in range(1, 8):
    day = TODAY - timedelta(days=i)
    # Generate 3 transactions per day
    for _ in range(3):
        amount = random.randint(2000, 5000)
        sql_statements.append(f"INSERT INTO sales (sale_date, amount) VALUES ('{day}', {amount});")

# 3. Rest of the Month (Random dates in current month)
# Start of current month
start_of_month = TODAY.replace(day=1)
# Generate 20 random transactions in this month
for _ in range(20):
    # Random day between start of month and today
    days_range = (TODAY - start_of_month).days
    if days_range > 0:
        random_day = start_of_month + timedelta(days=random.randint(0, days_range))
    else:
        random_day = TODAY
    
    amount = random.randint(1000, 10000)
    sql_statements.append(f"INSERT INTO sales (sale_date, amount) VALUES ('{random_day}', {amount});")

sql_statements.append("COMMIT;")

with open(SQL_FILE, "w") as f:
    f.write("\n".join(sql_statements))

print(f"Generated {len(sql_statements)} SQL statements in {SQL_FILE}")
