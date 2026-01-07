"""
Query Validator for Mr. Mark Chatbot
Validates query completeness, consistency, and permissions.
"""

from typing import Dict, Any, Tuple, Optional


def validate_query(params: Dict[str, Any], user_role: str, user_branch: Optional[int] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate query parameters for completeness and permissions.
    
    Args:
        params: Extracted parameters from parameter_extractor
        user_role: User's role (STAFF, MANAGER, ADMIN, OWNER)
        user_branch: User's assigned branch (for STAFF)
        
    Returns:
        (is_valid, error_message)
        - is_valid: True if query can be executed
        - error_message: None if valid, otherwise helpful error message
    """
    
    # --- 1. COMPLETENESS VALIDATION ---
    
    # Check if metric requires a period
    if params["metric"] == "average" and not params["period"]:
        return False, "Average of which period? Try: 'Average sales this month' or 'Average sales past 3 months'"
    
    # Check if period is specified for aggregate queries
    if params["metric"] in ["total", "sum"] and not params["period"] and not params["comparison"]:
        # If it's a simple "total sales" without context, ask for period
        if "sales" in params["raw_query"].lower() and len(params["raw_query"].split()) <= 3:
            return False, "Total sales for which period? Try: 'Today sales', 'This month sales', or 'Past 3 months'"
    
    # --- 2. CONSISTENCY VALIDATION ---
    
    # Check for conflicting parameters
    if params["comparison"] and params["comparison"]["type"] == "branch_vs_branch":
        # Comparison queries shouldn't also specify a single branch
        if params["branch"] and params["branch"] not in [params["comparison"]["branch1"], params["comparison"]["branch2"]]:
            return False, "Conflicting branch specifications in comparison query"
    
    # --- 3. PERMISSION VALIDATION ---
    
    # STAFF users cannot do comparisons
    if user_role == "STAFF" and params["comparison"]:
        return False, "Comparison queries are not available for your access level"
    
    # STAFF users cannot query other branches
    if user_role == "STAFF" and params["branch"]:
        if params["branch"] != user_branch and params["branch"] != "ALL":
            return False, f"You can only query Branch {user_branch}"
    
    # STAFF users cannot query "ALL" branches
    if user_role == "STAFF" and params["branch"] == "ALL":
        return False, "You can only query your assigned branch"
    
    # STAFF users cannot do ranking queries (highest/lowest branch)
    if user_role == "STAFF" and params["metric"] in ["highest", "lowest"]:
        if "branch" in params["raw_query"].lower():
            return False, "Branch ranking queries are not available for your access level"
    
    # --- 4. DATA AVAILABILITY VALIDATION ---
    
    # Check for future dates
    if params["period"] and params["period"].get("type") == "date":
        from datetime import datetime
        query_date = datetime.strptime(params["period"]["date"], "%Y-%m-%d").date()
        today = datetime.now().date()
        if query_date > today:
            return False, f"Cannot query future date: {params['period']['date']}"
    
    # Check for valid quarter
    if params["period"] and params["period"].get("type") == "quarter":
        if params["period"]["quarter"] not in [1, 2, 3, 4]:
            return False, f"Invalid quarter: {params['period']['quarter']}. Must be 1, 2, 3, or 4"
    
    # --- 5. ALL VALIDATIONS PASSED ---
    return True, None


def apply_defaults(params: Dict[str, Any], user_role: str, user_branch: Optional[int] = None) -> Dict[str, Any]:
    """
    Apply default values for missing parameters based on user role and query type.
    
    Args:
        params: Extracted parameters
        user_role: User's role
        user_branch: User's assigned branch
        
    Returns:
        Updated params with defaults applied
    """
    # Default branch logic
    if not params["branch"] and not params["comparison"]:
        if user_role == "STAFF":
            # STAFF always defaults to their branch
            params["branch"] = user_branch
        elif params["metric"] in ["total", "average"] and params["period"]:
            # Simple aggregate queries default to Branch 1
            params["branch"] = 1
        # Ranking queries (highest/lowest) don't need a default branch
    
    # Default period for certain metrics
    if params["metric"] == "growth" and not params["period"]:
        # Growth queries default to "this year vs last year"
        params["period"] = {"type": "year", "year": 2026}  # Current year
        params["comparison"] = {"type": "period_vs_period", "period1": "this_year", "period2": "last_year"}
    
    return params


def get_clarification_prompt(params: Dict[str, Any]) -> Optional[str]:
    """
    Generate helpful clarification prompt for ambiguous queries.
    
    Args:
        params: Extracted parameters
        
    Returns:
        Clarification prompt or None if query is clear
    """
    # Missing branch for non-ranking queries
    if not params["branch"] and not params["comparison"] and params["metric"] not in ["highest", "lowest"]:
        return "Which branch? Try: 'Branch 1', 'Branch 2', or 'All Branches'"
    
    # Missing period for average
    if params["metric"] == "average" and not params["period"]:
        return "Average of which period? Try: 'This month', 'Past 3 months', or 'This year'"
    
    # Ambiguous total
    if params["metric"] == "total" and not params["period"] and not params["comparison"]:
        return "Total sales for which period? Try: 'Today', 'This month', or 'Past 3 months'"
    
    return None


# Example usage
if __name__ == "__main__":
    from parameter_extractor import extract_parameters
    
    test_cases = [
        ("Average sales", "ADMIN", None),
        ("Total sales", "ADMIN", None),
        ("Compare Branch 1 and Branch 2", "STAFF", 1),
        ("Today sales", "STAFF", 1),
        ("Sales on 2026-12-31", "ADMIN", None),  # Future date
        ("Quarter 5 2025", "ADMIN", None),  # Invalid quarter
    ]
    
    print("Query Validation Tests:")
    print("-" * 80)
    for query, role, branch in test_cases:
        params = extract_parameters(query, role)
        is_valid, error = validate_query(params, role, branch)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"\n{status}: '{query}' (Role: {role})")
        if error:
            print(f"  Error: {error}")
