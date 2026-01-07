import re
import datetime
import calendar
from datetime import timedelta

def normalize_query(user_msg, user_role="staff", br_id=None):
    """
    Normalization Layer
    Input: Raw user natural language (e.g., "yesterday sales", "year summary 2025")
    Output: Canonical query string safe for main.py execution (e.g., "Sales on 2026-01-05")
    
    Principles:
    1. Resolve Relative Dates (Yesterday/Today) -> Concrete YYYY-MM-DD
    2. Resolve Ambiguous Aggregations -> Specific keywords (Total/Average)
    3. Safety Defaults -> If simple queries, ensure they match strict patterns.
    """
    
    clean_msg = user_msg.lower().strip()
    today = datetime.date.today()
    
    # --- 1. RELATIVE DATE NORMALIZATION ---
    
    # Extract branch info if present (to preserve it)
    branch_match = re.search(r'branch\s+(\d+)', clean_msg)
    branch_suffix = f" branch {branch_match.group(1)}" if branch_match else ""
    
    # "Yesterday"
    if "yesterday" in clean_msg:
        yesterday = today - timedelta(days=1)
        fmt_date = yesterday.strftime("%Y-%m-%d")
        # Rewrite to strict "Sales on YYYY-MM-DD" which main.py handles perfectly
        # Preserve "Average" if requested? Usually "Yesterday sales" implies Total.
        return f"Sales on {fmt_date}{branch_suffix}"

    # "Today"
    if "today" in clean_msg:
        fmt_date = today.strftime("%Y-%m-%d")
        return f"Sales on {fmt_date}{branch_suffix}"

    # "This Month"
    if "this month" in clean_msg:
        # Map to "Sales in <Month Name> <Year>"
        m_name = today.strftime("%B") # e.g. January
        year = today.year
        return f"Sales in {m_name} {year}"

    # "Last Month" / "Past Month"
    # (If user says "past month" without number, assume 1)
    if re.search(r'\b(last|past|previous)\s+month\b', clean_msg):
        # We could map this to "past 1 months" which triggers the rolling average/total logic
        if "average" in clean_msg:
             return "Average sales past 1 months"
        else:
             return "Total sales past 1 months"

    # --- 2. YEAR/PERIOD SUMMARY ---
    
    # "Year summary of 2025" or "2025 summary"
    # Existing main.py handles "Total sales in 2025" well.
    year_match = re.search(r'year\s+summary.*?(202\d)', clean_msg)
    if year_match:
        target_year = year_match.group(1)
        return f"Total sales in {target_year}"
    
    # Just "sales in 2025" -> "Total sales in 2025"
    # (Fixes cases where 'Total' is omitted and might confuse logic)
    if re.fullmatch(r'sales\s+in\s+(202\d)', clean_msg):
        return f"Total sales in {clean_msg.split()[-1]}"

    # --- 3. METRIC NORMALIZATION ---

    # "Average of ..." without "Sales"
    # "Average 2025" -> "Average sales 2025"
    if "average" in clean_msg and "sales" not in clean_msg:
         return clean_msg.replace("average", "average sales")
    
    # --- 4. QUARTER NORMALIZATION ---
    
    # "Q1 2025", "Quarter 1 2025", "First quarter 2025"
    quarter_patterns = [
        (r'\bq1\b', 'Quarter 1'),
        (r'\bq2\b', 'Quarter 2'),
        (r'\bq3\b', 'Quarter 3'),
        (r'\bq4\b', 'Quarter 4'),
        (r'\bfirst quarter\b', 'Quarter 1'),
        (r'\bsecond quarter\b', 'Quarter 2'),
        (r'\bthird quarter\b', 'Quarter 3'),
        (r'\bfourth quarter\b', 'Quarter 4'),
        (r'\bquarter 1\b', 'Quarter 1'),
        (r'\bquarter 2\b', 'Quarter 2'),
        (r'\bquarter 3\b', 'Quarter 3'),
        (r'\bquarter 4\b', 'Quarter 4'),
    ]
    
    for pattern, replacement in quarter_patterns:
        if re.search(pattern, clean_msg):
            # Extract year if present
            year_match = re.search(r'(202\d)', clean_msg)
            year = year_match.group(1) if year_match else str(today.year)
            return f"{replacement} {year}{branch_suffix}"
    
    # --- 5. WEEK NORMALIZATION ---
    
    # "This week"
    if "this week" in clean_msg:
        # Get Monday of current week
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)
        return f"Week {monday.strftime('%Y-%m-%d')} to {sunday.strftime('%Y-%m-%d')}{branch_suffix}"
    
    # "Last week"
    if "last week" in clean_msg or "past week" in clean_msg:
        days_since_monday = today.weekday()
        this_monday = today - timedelta(days=days_since_monday)
        last_monday = this_monday - timedelta(days=7)
        last_sunday = last_monday + timedelta(days=6)
        return f"Week {last_monday.strftime('%Y-%m-%d')} to {last_sunday.strftime('%Y-%m-%d')}{branch_suffix}"
    
    # --- 6. DATE RANGE NORMALIZATION ---
    
    # "January to March", "Jan to Mar", "January-March"
    month_names = {
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12,
    }
    
    # Pattern: "month1 to month2" or "month1-month2"
    range_pattern = r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\s*(?:to|-)\s*(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)'
    range_match = re.search(range_pattern, clean_msg)
    
    if range_match:
        start_month_name = range_match.group(1)
        end_month_name = range_match.group(2)
        start_month = month_names[start_month_name]
        end_month = month_names[end_month_name]
        
        # Extract year if present
        year_match = re.search(r'(202\d)', clean_msg)
        year = int(year_match.group(1)) if year_match else today.year
        
        # Get last day of end month
        _, last_day = calendar.monthrange(year, end_month)
        
        start_date = f"{year}-{start_month:02d}-01"
        end_date = f"{year}-{end_month:02d}-{last_day}"
        
        return f"Date range {start_date} to {end_date}{branch_suffix}"
    
    # "First half of 2025" -> Jan to Jun
    if "first half" in clean_msg:
        year_match = re.search(r'(202\d)', clean_msg)
        year = int(year_match.group(1)) if year_match else today.year
        return f"Date range {year}-01-01 to {year}-06-30{branch_suffix}"
    
    # "Second half of 2025" -> Jul to Dec
    if "second half" in clean_msg:
        year_match = re.search(r'(202\d)', clean_msg)
        year = int(year_match.group(1)) if year_match else today.year
        return f"Date range {year}-07-01 to {year}-12-31{branch_suffix}"
         
    # --- 7. DEFAULT PASSTHROUGH ---
    return user_msg
