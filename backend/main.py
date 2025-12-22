from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import re # Added regex support

# ===============================
# APP SETUP
# ===============================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# MODELS
# ===============================
class ChatRequest(BaseModel):
    message: str


# ===============================
# INTENT DETECTION (FIXED)
# ===============================
def detect_period(text: str):
    text = text.lower()

    if "yesterday" in text:
        return "yesterday"

    if "last week" in text or "previous week" in text or "past week" in text:
        return "week"

    if "today" in text or "daily" in text:
        return "day"

    if "month" in text:
        return "month"

    if "year" in text:
        return "year"

    return None


# ===============================
# ERP API CALL (MATCHES POSTMAN)
# ===============================
def fetch_live_sales(period="day", year="2025", br_id=1):
    url = "https://api.emark.live/api/mobile/sales"

    headers = {
        "X-Forwarded-For": "144.76.94.137"
    }

    payload = {
        "db": "84",
        "br_id": str(br_id), # Added branch ID
        "year": year,
        "type": "daily",
        "range": "1"
    }

    if period == "week":
        payload["range"] = "7"

    elif period == "month":
        payload["type"] = "monthly"
        payload["range"] = "1"

    elif period == "year":
        payload["type"] = "monthly"
        payload["range"] = "12"

    try:
        # 'data=' sends it as form-data (correct for your ERP)
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        
        # If the ERP is overwhelmed (429), tell the user to wait
        if response.status_code == 429:
             print("❌ ERP Rate Limit (429)")
             return {"total": 0, "error": "Rate limited. Please wait 60 seconds."}

        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        
        if response.status_code == 200:
            data = response.json()
            print("🔥 ERP RAW RESPONSE:", data)
            # API might return multiple days (e.g. yesterday + today) even with range=1
            # Filter STRICTLY for today's date
            today_str = date.today().strftime("%Y-%m-%d")
            
            total_val = 0.0
            if "data" in data and isinstance(data.get("data"), list):
                for row in data["data"]:
                    # period comes as "YYYY-MM-DD"
                    if row.get("period") == today_str:
                        val = float(row.get("total_sales", row.get("total_sale", 0)))
                        total_val += val
                        
            return {"total": round(total_val, 2)}

    except requests.exceptions.HTTPError as e:
        print(f"ERP Server Error: {e.response.status_code}")
        return {"total": 0, "error": f"ERP Server Error: {e.response.status_code}"}
        
    except Exception as e:
        print(f"API Error: {e}")
        return {"total": 0, "error": f"Connection Error: {str(e)}"}


# ===============================
# CHAT ENDPOINT (FINAL)
# ===============================
# ===============================
# DATE PARSING & DB
# ===============================
import psycopg2
from datetime import datetime, timedelta, date
import calendar

# Global Month Map with Common Typos
MONTH_ALIASES = {
    # Standard & Short
    "january": 1, "jan": 1, 
    "february": 2, "feb": 2, 
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8, 
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10, 
    "november": 11, "nov": 11, 
    "december": 12, "dec": 12,

    # Common Typos
    "janury": 1, "jannuary": 1,
    "febuary": 2, "febrary": 2, "februry": 2,
    "augest": 8,
    "septamber": 9, "septmber": 9, "septermber": 9,
    "octomber": 10,
    "novembar": 11, "novemeber": 11,
    "decamber": 12, "desember": 12, "decemeber": 12
}

def get_db():
    try:
        return psycopg2.connect(
            host="db", # Docker service name
            database="marksolution",
            user="markuser",
            password="markpass"
        )
    except:
        return None

def fetch_from_db(target_date, br_id=1):
    """
    Fetches sales from local DB for a specific date and branch.
    format: YYYY-MM-DD
    """
    conn = get_db()
    if not conn: 
        print("❌ DEBUG: Database connection failed!")
        return None
    
    try:
        cur = conn.cursor()
        # Filter by br_id
        query = "SELECT amount FROM sales WHERE sale_date = %s AND br_id = %s"
        cur.execute(query, (target_date, br_id))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            return float(row[0])
        else:
            return None
    except Exception as e:
        print(f"❌ DB Error: {e}")
        return None

def fetch_monthly_sum_from_db(year, month_num, br_id=1):
    """
    Calculates total sales for a specific month from the local DB.
    """
    conn = get_db()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        # Calculate start and end date of the month
        # Last day of month
        _, last_day = calendar.monthrange(year, month_num)
        start_date = f"{year}-{month_num:02d}-01"
        end_date = f"{year}-{month_num:02d}-{last_day}"
        
        query = "SELECT SUM(amount) FROM sales WHERE sale_date >= %s AND sale_date <= %s AND br_id = %s"
        cur.execute(query, (start_date, end_date, br_id))
        row = cur.fetchone()
        
        cur.close()
        conn.close()
        
        # row[0] will be None if no records sum up
        return float(row[0]) if row and row[0] is not None else 0.0
        
    except Exception as e:
        print(f"❌ DB Sum Error: {e}")
        return None

def fetch_monthly_average(year, month_num, br_id=1):
    """
    Calculates average daily sales for a specific month from the local DB.
    Since we sync monthly totals (1 row per month), we must divide Total by DaysInMonth manually.
    """
    conn = get_db()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        _, last_day = calendar.monthrange(year, month_num)
        start_date = f"{year}-{month_num:02d}-01"
        end_date = f"{year}-{month_num:02d}-{last_day}"
        
        # Calculate Average: MonthlyTotal / DaysInMonth
        query = "SELECT SUM(amount) FROM sales WHERE sale_date >= %s AND sale_date <= %s AND br_id = %s"
        cur.execute(query, (start_date, end_date, br_id))
        row = cur.fetchone()
        
        cur.close()
        conn.close()
        
        total = float(row[0]) if row and row[0] is not None else 0.0
        return total / last_day
        
    except Exception as e:
        print(f"❌ DB Avg Error: {e}")
        return None

def fetch_year_total(year, br_id=1):
    """
    Calculates total sales for the entire year.
    """
    conn = get_db()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        query = "SELECT SUM(amount) FROM sales WHERE sale_date >= %s AND sale_date <= %s AND br_id = %s"
        cur.execute(query, (start_date, end_date, br_id))
        row = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return float(row[0]) if row and row[0] is not None else 0.0
    except Exception as e:
        print(f"❌ DB Year Total Error: {e}")
        return None

def find_extreme_month(year=2025, mode='max', br_id=1):
    """
    Finds the month with the highest or lowest total sales in the given year.
    mode: 'max' for highest, 'min' for lowest.
    Returns (month_name, total_amount).
    """
    conn = get_db()
    if not conn:
        return None, 0.0
    
    try:
        cur = conn.cursor()
        
        order = "DESC" if mode == 'max' else "ASC"
        
        query = f"""
            SELECT EXTRACT(MONTH FROM sale_date) as m, SUM(amount) as total
            FROM sales
            WHERE EXTRACT(YEAR FROM sale_date) = %s AND br_id = %s
            GROUP BY m
            ORDER BY total {order}
            LIMIT 1
        """
        cur.execute(query, (year, br_id))
        row = cur.fetchone() # (month_num, total)
        
        cur.close()
        conn.close()
        
        if row:
            m_num = int(row[0])
            total = float(row[1])
            m_name = calendar.month_name[m_num]
            return m_name, total
        
        return None, 0.0
        
    except Exception as e:
        print(f"❌ DB Extreme Month Error: {e}")
        return None, 0.0

def extract_two_months(text):
    """
    Finds two distinct months in the text for comparison.
    Returns [(name1, num1), (name2, num2)] or None.
    """
    text = text.lower()
    found = []
    
    # Iterate through all aliases
    # To avoid matching 'jan' inside 'january', we rely on \b boundaries
    # Complexity: simple scan.
    
    # We need to collect unique months (by number)
    seen_nums = set()
    
    # We iterate aliases, but order matters? Not really if we check all.
    for m_name, m_num in MONTH_ALIASES.items():
        if m_num in seen_nums:
            continue
            
        if re.search(fr'\b{m_name}\b', text):
            full_name = calendar.month_name[m_num]
            found.append((full_name, m_num))
            seen_nums.add(m_num)
            
            if len(found) == 2:
                break
    
    return found if len(found) == 2 else None

def extract_all_months(text):
    """
    Finds ALL unique months in the text.
    Returns list of [(name, num), ...]
    """
    text = text.lower()
    found = []
    seen_nums = set()
    
    # We iterate aliases
    for m_name, m_num in MONTH_ALIASES.items():
        if m_num in seen_nums:
            continue
            
        if re.search(fr'\b{m_name}\b', text):
            full_name = calendar.month_name[m_num]
            found.append((full_name, m_num))
            seen_nums.add(m_num)
    
    # Sort by month number for logical display
    found.sort(key=lambda x: x[1])
    return found

def get_past_months(count, ref_date=None):
    """
    Returns a list of (month_name, month_num) for the last 'count' months.
    Excludes current partial month? Usually 'past 3 months' implies [Last Month, Month-before, Month-before].
    Let's assume inclusive of current month if not specified, 
    but typically financial 'past 3 months' means completed months or rolling window.
    Given "Dec 22" context, let's include December as it has data.
    """
    if ref_date is None:
        ref_date = date(2025, 12, 22) # Mocking 'today' as per prompt context
        
    result = []
    current_m = ref_date.month
    current_y = ref_date.year
    
    for _ in range(count):
        # Add current matching month
        name = calendar.month_name[current_m]
        result.append((name, current_m))
        
        # Move back one month
        current_m -= 1
        if current_m < 1:
            current_m = 12
            current_y -= 1
            
    # Return in chronological order (oldest first)
    return result[::-1]

def extract_goal_amount(text):
    """
    Extracts a monetary goal from text.
    Supports: "100 million", "2.5M", "1 billion", "500,000"
    Returns float or None.
    """
    text = text.lower().replace(",", "")
    
    # 1. Look for explicit multipliers
    # Regex for number followed by optional space and million/billion/m/b
    # Groups: 1=number, 3=multiplier
    match = re.search(r'(\d+(\.\d+)?)\s*(million|billion|lakh|crore|m|b|k)', text)
    
    if match:
        amount = float(match.group(1))
        unit = match.group(3)
        
        if unit in ["million", "m"]:
            return amount * 1_000_000
        elif unit in ["billion", "b"]:
            return amount * 1_000_000_000
        elif unit in ["lakh"]:
            return amount * 100_000
        elif unit in ["crore"]:
            return amount * 10_000_000
        elif unit in ["k"]:
            return amount * 1_000
            
    # 2. Look for raw huge numbers (e.g. 100000000)
    # Simple regex for large numbers (at least 5 digits to avoid conflict with dates/small nums)
    match_raw = re.search(r'(\d{5,})', text)
    if match_raw:
        return float(match_raw.group(1))
        
    return None

def extract_date(text):
    """
    Parses 'Jan 1st', 'January 10', '2025-01-01'.
    """
    text = text.lower()
    
    # 1. YYYY-MM-DD
    match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
    if match: return match.group(1)
    
    # 2. Key-based search using generic map
    # Matches "jan 1", "january 23", "decamber 5"
    
    for month_name, month_num in MONTH_ALIASES.items():
        if month_name in text:
            # Find the number following the month
            # Look for: "jan" followed by space then digits
            # Regex: jan.*?(\d+)
            day_match = re.search(fr'{month_name}.*?\b(\d+)(st|nd|rd|th)?\b', text)
            if day_match:
                day = int(day_match.group(1))
                return f"2025-{month_num:02d}-{day:02d}"
    
    return None

def extract_month_only(text):
    """
    Detects if a user is asking about a specific month (without a day).
    Returns (month_name_full, month_number_int).
    """
    text = text.lower()
    
    for m_name, m_num in MONTH_ALIASES.items():
        # strict check to avoid partial matches if necessary, but 'in text' is usually okay 
        # provided we checked for specific dates first (which we will).
        # We use \b to ensure we match 'jan' but not 'jane'.
        if re.search(fr'\b{m_name}\b', text):
            # Return standard Full Name based on num
            full_name = calendar.month_name[m_num]
            return full_name, m_num
            
    return None

def extract_branch(text):
    """
    Extracts branch ID from text. Default is 1.
    Looks for "Branch X", "Goal", "br_id X".
    """
    text = text.lower()
    match = re.search(r'branch\s*(\d+)', text)
    if match:
        return int(match.group(1))
    return 1

# ===============================
# CHAT ENDPOINT (FINAL)
# ===============================
@app.post("/chat")
def chat(req: ChatRequest):
    user_msg = req.message.strip()
    
    # Extract Branch ID (Defaults to 1)
    br_id = extract_branch(user_msg)

    # Greeting
    if user_msg.lower() in ["hi", "hello", "hey"]:
        return {
            "answer": "Hello! I am the MarkSolution Enterprise Assistant. How can I help you?"
        }

    # PRIORITY 0: Advanced Analytics
    
    # 0. Goal/Target Analysis ("goal", "target")
    if any(k in user_msg.lower() for k in ["goal", "target", "aim", "need to earn"]):
         target_amount = extract_goal_amount(user_msg)
         if target_amount:
             ytd = fetch_year_total(2025, br_id) or 0.0
             
             diff = ytd - target_amount
             
             if diff >= 0:
                 return {"answer": f"We have already exceeded our goal of {target_amount:,.2f} LKR! Current YTD is {ytd:,.2f} LKR (Surplus: {diff:,.2f} LKR)."}
             else:
                 needed = abs(diff)
                 return {"answer": f"To reach our goal of {target_amount:,.2f} LKR, we need to earn {needed:,.2f} LKR more. (Current YTD: {ytd:,.2f} LKR)"}
    
    # 1. Comparison ("compare", "difference", "vs")
    if any(k in user_msg.lower() for k in ["compare", "difference", "vs", "more than", "less than"]):
         months = extract_two_months(user_msg)
         if months:
             (m1_name, m1_num), (m2_name, m2_num) = months
             val1 = fetch_monthly_sum_from_db(2025, m1_num, br_id)
             val2 = fetch_monthly_sum_from_db(2025, m2_num, br_id)
             
             diff = val1 - val2
             more_less = "more" if diff >= 0 else "less"
             
             return {"answer": f"We earned {abs(diff):,.2f} LKR {more_less} in {m1_name} compared to {m2_name}."}

    # 1.1 Multi-Month Summary ("Jan and Feb", "Past 3 months")
    # Priority: Must check this before "Average" to avoid confusion, and AFTER "Compare" (handled above).
    
    # Check for "past X months"
    past_match = re.search(r'past (\d+) months', user_msg.lower())
    target_months = []
    
    if past_match:
        count = int(past_match.group(1))
        target_months = get_past_months(count)
    else:
        # Check for explicit multiple months (if count >= 2 and NOT comparing)
        detected_months = extract_all_months(user_msg)
        if len(detected_months) >= 2:
            target_months = detected_months

    if target_months:
        total_agg = 0.0
        breakdown_parts = []
        
        for m_name, m_num in target_months:
            val = fetch_monthly_sum_from_db(2025, m_num, br_id)
            total_agg += val
            breakdown_parts.append(f"{m_name}: {val:,.2f} LKR")
            
        breakdown_str = " | ".join(breakdown_parts)
        month_names_str = ", ".join([m[0] for m in target_months])
        
        return {
            "answer": (
                f"Financial Summary for {month_names_str} (Branch {br_id}):\n"
                f"**Grand Total: {total_agg:,.2f} LKR**\n\n"
                f"Breakdown:\n{breakdown_str}"
            )
        }

    # 2. Average ("average", "daily income")
    if any(k in user_msg.lower() for k in ["average", "daily income", "avg"]):
         month_info = extract_month_only(user_msg)
         if month_info:
             m_name, m_num = month_info
             avg_val = fetch_monthly_average(2025, m_num, br_id)
             if avg_val is not None:
                 return {"answer": f"The average daily income in {m_name} 2025 (Branch {br_id}) was {avg_val:,.2f} LKR."}

    # 3. YTD ("year to date", "total sales for the year", "2025 total")
    if any(k in user_msg.lower() for k in ["year total", "sales for the year", "2025 total", "total sales of 2025"]):
         ytd = fetch_year_total(2025, br_id)
         if ytd is not None:
             return {"answer": f"Our total sales for the year 2025 (Branch {br_id}) so far is {ytd:,.2f} LKR."}

    # 4. Best/Highest/Lowest Month
    if any(k in user_msg.lower() for k in ["highest", "best month", "most sales", "peak"]):
         best_month, best_total = find_extreme_month(2025, mode='max', br_id=br_id)
         if best_month:
             return {"answer": f"The highest sales month in 2025 (Branch {br_id}) was {best_month} with {best_total:,.2f} LKR."}

    if any(k in user_msg.lower() for k in ["lowest", "minimum", "least sales", "worst"]):
         worst_month, worst_total = find_extreme_month(2025, mode='min', br_id=br_id)
         if worst_month:
             return {"answer": f"The lowest sales month in 2025 (Branch {br_id}) was {worst_month} with {worst_total:,.2f} LKR."}

    # 5. Real-Time / Current Sales ("now", "current")
    if any(k in user_msg.lower() for k in ["now", "current", "right now", "at the moment"]):
         # Bypass DB, force API call for 'today'
         sales = fetch_live_sales('day', br_id=br_id)
         if "error" in sales:
             return {"answer": f"System Alert: {sales['error']}"}
         
         return {"answer": f"The current sales status for Branch {br_id} is {sales['total']:,} LKR."}

    # PRIORITY 1: Specific Date (e.g. "Jan 7th")
    # We check this first because "Jan 7" contains "Jan", which would also trigger the month check.
    
    # 1.1 explicit "tomorrow" check
    if "tomorrow" in user_msg.lower() or "next week" in user_msg.lower():
         return {"answer": "I cannot tell it"}

    try:
        specific_date = extract_date(user_msg)
        if specific_date:
            # Future Check
            date_obj = datetime.strptime(specific_date, "%Y-%m-%d").date()
            if date_obj > datetime.now().date():
                 return {"answer": "I cannot tell it"}

            val = fetch_from_db(specific_date, br_id)
            if val is not None:
                 return {"answer": f"On {specific_date} (Branch {br_id}), we earned {val:,.2f} LKR."}
            else:
                 return {"answer": f"I couldn't find any sales data for {specific_date} in our database."}
    except Exception as e:
        print(f"❌ Date Extraction Error: {e}")
        # Continue to other checks if this fails

    # PRIORITY 2: Specific Month (e.g. "January sales")
    # Only if no specific date was found (or valid).
    month_info = extract_month_only(user_msg)
    if month_info:
        m_name, m_num = month_info
        # Default year 2025
        total_month = fetch_monthly_sum_from_db(2025, m_num, br_id)
        if total_month is not None:
             return {"answer": f"In {m_name} 2025 (Branch {br_id}), the total sales summary is {total_month:,.2f} LKR."}
        else:
             return {"answer": f"I couldn't calculate sales for {m_name}."}

    # PRIORITY 2.5: Yesterday Explicit (DB)
    # User requested to calculate yesterday's date and fetch from DB
    if "yesterday" in user_msg.lower():
        yesterday_date = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday_date.strftime('%Y-%m-%d')
        
        val = fetch_from_db(yesterday_str, br_id)
        if val is not None:
             return {"answer": f"We earned {val:,.2f} LKR yesterday ({yesterday_str}) for Branch {br_id}."}
        else:
             return {"answer": f"I couldn't find sales data for yesterday ({yesterday_str})."}

    # PRIORITY 3: Standard Live Periods (API)
    period = detect_period(user_msg)
    if period:
        sales = fetch_live_sales(period)

        if "error" in sales:
             return {"answer": f"System Alert: {sales['error']}"}

        if sales["total"] > 0:
            label_map = {
                "day": "today",
                "yesterday": "yesterday",
                "week": "last week",
                "month": "this month",
                "year": "this year"
            }
            label = label_map.get(period, "this period")
            return {"answer": f"We earned {sales['total']:,} LKR {label}."}
        else:
            return {"answer": f"The ERP reported 0 sales for {period}. (Raw Response: {sales})"}

    return {
        "answer": "I don’t know about this yet. Try asking 'yesterday', 'last week', or 'Jan 1st'."
    }
