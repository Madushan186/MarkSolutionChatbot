"""
Parameter Extractor for Mr. Mark Chatbot
Extracts structured parameters from normalized queries.
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime


def extract_parameters(normalized_query: str, user_role: str = "STAFF") -> Dict[str, Any]:
    """
    Extract structured parameters from normalized query.
    
    Args:
        normalized_query: Query after normalization
        user_role: User's role for context
        
    Returns:
        Dictionary with: metric, period, branch, comparison
    """
    query_lower = normalized_query.lower()
    
    params = {
        "metric": None,
        "period": None,
        "branch": None,
        "comparison": None,
        "raw_query": normalized_query
    }
    
    # --- 1. EXTRACT METRIC ---
    params["metric"] = extract_metric(query_lower)
    
    # --- 2. EXTRACT PERIOD ---
    params["period"] = extract_period(normalized_query)
    
    # --- 3. EXTRACT BRANCH ---
    params["branch"] = extract_branch(query_lower)
    
    # --- 4. EXTRACT COMPARISON ---
    params["comparison"] = extract_comparison(query_lower)
    
    return params


def extract_metric(query: str) -> str:
    """Extract metric type from query."""
    if "average" in query or "mean" in query:
        return "average"
    elif "highest" in query or "maximum" in query or "max" in query or "best" in query or "top" in query:
        return "highest"
    elif "lowest" in query or "minimum" in query or "min" in query or "worst" in query or "bottom" in query:
        return "lowest"
    elif "growth" in query or "increase" in query or "decrease" in query or "change" in query:
        return "growth"
    elif "total" in query or "sum" in query:
        return "total"
    else:
        # Default to total for simple queries
        return "total"


def extract_period(query: str) -> Optional[Dict[str, Any]]:
    """
    Extract period information from query.
    
    Returns dict with:
        - type: "date" | "month" | "quarter" | "year" | "week" | "range" | "past_n"
        - Additional fields based on type
    """
    query_lower = query.lower()
    
    # Specific date: "Sales on 2026-01-07"
    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', query)
    if date_match:
        return {
            "type": "date",
            "date": date_match.group(0),
            "year": int(date_match.group(1)),
            "month": int(date_match.group(2)),
            "day": int(date_match.group(3))
        }
    
    # Quarter: "Quarter 1 2025"
    quarter_match = re.search(r'quarter (\d) (\d{4})', query_lower)
    if quarter_match:
        return {
            "type": "quarter",
            "quarter": int(quarter_match.group(1)),
            "year": int(quarter_match.group(2))
        }
    
    # Week: "Week 2026-01-06 to 2026-01-12"
    week_match = re.search(r'week (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})', query_lower)
    if week_match:
        return {
            "type": "week",
            "start_date": week_match.group(1),
            "end_date": week_match.group(2)
        }
    
    # Date range: "Date range 2025-01-01 to 2025-03-31"
    range_match = re.search(r'date range (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})', query_lower)
    if range_match:
        return {
            "type": "range",
            "start_date": range_match.group(1),
            "end_date": range_match.group(2)
        }
    
    # Past N months: "Past 3 months"
    past_match = re.search(r'past (\d+) months?', query_lower)
    if past_match:
        return {
            "type": "past_n",
            "count": int(past_match.group(1)),
            "unit": "months"
        }
    
    # Specific month: "Sales in June 2025"
    month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                   'july', 'august', 'september', 'october', 'november', 'december']
    for idx, month_name in enumerate(month_names, 1):
        if month_name in query_lower:
            year_match = re.search(r'(\d{4})', query)
            if year_match:
                return {
                    "type": "month",
                    "month": idx,
                    "month_name": month_name.capitalize(),
                    "year": int(year_match.group(1))
                }
    
    # Year: "2025" or "in 2025"
    year_match = re.search(r'\b(202\d)\b', query)
    if year_match and ("total" in query_lower or "year" in query_lower or "in " + year_match.group(1) in query_lower):
        return {
            "type": "year",
            "year": int(year_match.group(1))
        }
    
    return None


def extract_branch(query: str) -> Optional[Any]:
    """Extract branch information from query."""
    # "All Branches"
    if "all branches" in query or "all branch" in query:
        return "ALL"
    
    # "Branch 1", "Branch 2", etc.
    branch_match = re.search(r'branch (\d+)', query)
    if branch_match:
        return int(branch_match.group(1))
    
    return None


def extract_comparison(query: str) -> Optional[Dict[str, Any]]:
    """
    Extract comparison parameters.
    
    Returns dict with:
        - type: "branch_vs_branch" | "period_vs_period"
        - entity1, entity2
    """
    # Branch comparison: "Branch 1 vs Branch 2" or "Compare Branch 1 and Branch 2"
    branch_comp_match = re.search(r'branch (\d+).*?(?:vs|and|versus|compared to).*?branch (\d+)', query)
    if branch_comp_match:
        return {
            "type": "branch_vs_branch",
            "branch1": int(branch_comp_match.group(1)),
            "branch2": int(branch_comp_match.group(2))
        }
    
    # Period comparison: "This month vs last month"
    if "this month" in query and "last month" in query:
        return {
            "type": "period_vs_period",
            "period1": "this_month",
            "period2": "last_month"
        }
    
    return None


# Example usage
if __name__ == "__main__":
    test_queries = [
        "Sales on 2026-01-07",
        "Quarter 1 2025",
        "Week 2026-01-06 to 2026-01-12",
        "Date range 2025-01-01 to 2025-03-31",
        "Past 3 months",
        "Sales in June 2025",
        "Total sales in 2025",
        "Average sales for Branch 1",
        "Compare Branch 1 and Branch 2",
        "Highest performing branch this month"
    ]
    
    print("Parameter Extraction Tests:")
    print("-" * 80)
    for query in test_queries:
        params = extract_parameters(query)
        print(f"\nQuery: '{query}'")
        print(f"  Metric: {params['metric']}")
        print(f"  Period: {params['period']}")
        print(f"  Branch: {params['branch']}")
        print(f"  Comparison: {params['comparison']}")
