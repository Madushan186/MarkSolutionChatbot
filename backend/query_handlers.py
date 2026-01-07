"""
Query Handlers for Mr. Mark Chatbot
Handlers for Quarter, Week, Range, and Growth queries.
"""

import calendar
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple


def handle_quarter_query(quarter: int, year: int, br_id: Any, fetch_monthly_sum_fn) -> Tuple[List, float]:
    """
    Handle quarter queries (Q1, Q2, Q3, Q4).
    
    Args:
        quarter: Quarter number (1-4)
        year: Year
        br_id: Branch ID
        fetch_monthly_sum_fn: Function to fetch monthly sum from DB
        
    Returns:
        (rows, total) for table display
    """
    # Map quarter to months
    quarter_months = {
        1: [1, 2, 3],    # Q1: Jan, Feb, Mar
        2: [4, 5, 6],    # Q2: Apr, May, Jun
        3: [7, 8, 9],    # Q3: Jul, Aug, Sep
        4: [10, 11, 12]  # Q4: Oct, Nov, Dec
    }
    
    months = quarter_months[quarter]
    month_names = [calendar.month_name[m] for m in months]
    
    rows = []
    total = 0.0
    
    for month_num, month_name in zip(months, month_names):
        amount = fetch_monthly_sum_fn(year, month_num, br_id)
        rows.append([f"{month_name} {year}", f"{amount:,.2f}"])
        total += amount
    
    return rows, total


def handle_week_query(start_date: str, end_date: str, br_id: Any, fetch_daily_sales_fn) -> Tuple[List, float]:
    """
    Handle week queries.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        br_id: Branch ID
        fetch_daily_sales_fn: Function to fetch daily sales from DB
        
    Returns:
        (rows, total) for table display
    """
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    rows = []
    total = 0.0
    current_date = start
    
    while current_date <= end:
        date_str = current_date.strftime("%Y-%m-%d")
        amount = fetch_daily_sales_fn(date_str, br_id)
        
        # Format: "Monday, Jan 06"
        day_name = current_date.strftime("%A")
        date_display = current_date.strftime("%b %d")
        
        rows.append([f"{day_name}, {date_display}", f"{amount:,.2f}"])
        total += amount
        current_date += timedelta(days=1)
    
    return rows, total


def handle_range_query(start_date: str, end_date: str, br_id: Any, fetch_monthly_sum_fn) -> Tuple[List, float]:
    """
    Handle date range queries (group by month for readability).
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        br_id: Branch ID
        fetch_monthly_sum_fn: Function to fetch monthly sum from DB
        
    Returns:
        (rows, total) for table display
    """
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    rows = []
    total = 0.0
    
    # Group by months in the range
    current_date = start.replace(day=1)  # Start of first month
    
    while current_date <= end:
        year = current_date.year
        month = current_date.month
        month_name = calendar.month_name[month]
        
        amount = fetch_monthly_sum_fn(year, month, br_id)
        rows.append([f"{month_name} {year}", f"{amount:,.2f}"])
        total += amount
        
        # Move to next month
        if month == 12:
            current_date = current_date.replace(year=year+1, month=1)
        else:
            current_date = current_date.replace(month=month+1)
    
    return rows, total


def handle_growth_query(period1: Dict, period2: Dict, br_id: Any, fetch_for_period_fn) -> Dict[str, Any]:
    """
    Handle growth/trend queries.
    
    Args:
        period1: Current period (dict with type and details)
        period2: Comparison period (dict with type and details)
        br_id: Branch ID
        fetch_for_period_fn: Function to fetch sales for any period type
        
    Returns:
        Dict with growth_pct, val1, val2, period1_label, period2_label
    """
    val1 = fetch_for_period_fn(period1, br_id)
    val2 = fetch_for_period_fn(period2, br_id)
    
    if val2 > 0:
        growth_pct = ((val1 - val2) / val2) * 100
    else:
        growth_pct = 0.0
    
    return {
        "growth_pct": growth_pct,
        "val1": val1,
        "val2": val2,
        "period1_label": format_period_label(period1),
        "period2_label": format_period_label(period2)
    }


def format_period_label(period: Dict) -> str:
    """Format period dict into human-readable label."""
    if period["type"] == "date":
        return period["date"]
    elif period["type"] == "month":
        return f"{period['month_name']} {period['year']}"
    elif period["type"] == "quarter":
        return f"Q{period['quarter']} {period['year']}"
    elif period["type"] == "year":
        return str(period["year"])
    elif period["type"] == "week":
        return f"Week {period['start_date']}"
    elif period["type"] == "range":
        return f"{period['start_date']} to {period['end_date']}"
    elif period["type"] == "past_n":
        return f"Past {period['count']} {period['unit']}"
    else:
        return "Unknown period"


def get_quarter_months(quarter: int) -> List[int]:
    """Get list of month numbers for a quarter."""
    quarter_months = {
        1: [1, 2, 3],
        2: [4, 5, 6],
        3: [7, 8, 9],
        4: [10, 11, 12]
    }
    return quarter_months.get(quarter, [])


# Example usage
if __name__ == "__main__":
    # Mock functions for testing
    def mock_fetch_monthly(year, month, br_id):
        return 1000000.0 * month  # Mock data
    
    def mock_fetch_daily(date, br_id):
        return 50000.0  # Mock data
    
    print("Handler Tests:")
    print("-" * 80)
    
    # Test quarter handler
    print("\n1. Quarter Handler (Q1 2025):")
    rows, total = handle_quarter_query(1, 2025, 1, mock_fetch_monthly)
    for row in rows:
        print(f"  {row[0]}: {row[1]}")
    print(f"  Total: {total:,.2f}")
    
    # Test week handler
    print("\n2. Week Handler (2026-01-06 to 2026-01-12):")
    rows, total = handle_week_query("2026-01-06", "2026-01-12", 1, mock_fetch_daily)
    for row in rows[:3]:  # Show first 3 days
        print(f"  {row[0]}: {row[1]}")
    print(f"  ... Total: {total:,.2f}")
    
    # Test range handler
    print("\n3. Range Handler (Jan-Mar 2025):")
    rows, total = handle_range_query("2025-01-01", "2025-03-31", 1, mock_fetch_monthly)
    for row in rows:
        print(f"  {row[0]}: {row[1]}")
    print(f"  Total: {total:,.2f}")
