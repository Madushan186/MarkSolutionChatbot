"""
Intent Classifier for Mr. Mark Chatbot
Classifies user queries into 5 intent types for accurate handling.
"""

import re
from typing import Literal

IntentType = Literal["SINGLE_POINT", "AGGREGATE", "COMPARISON", "RANKING", "TREND"]


def classify_intent(query: str) -> IntentType:
    """
    Classify user query into one of 5 intent types.
    
    Args:
        query: Normalized user query string
        
    Returns:
        Intent type: SINGLE_POINT | AGGREGATE | COMPARISON | RANKING | TREND
    """
    query_lower = query.lower()
    
    # 1. COMPARISON - Comparing two entities
    comparison_keywords = [
        "compare", " vs ", " versus ", "compared to", "difference between",
        "branch 1 and branch 2", "branch 2 and branch 1",
        "this month vs last month", "last month vs this month"
    ]
    if any(keyword in query_lower for keyword in comparison_keywords):
        return "COMPARISON"
    
    # 2. RANKING - Finding best/worst
    ranking_keywords = [
        "highest", "lowest", "best", "worst", "top", "bottom",
        "most", "least", "maximum", "minimum",
        "which branch has", "what branch has"
    ]
    if any(keyword in query_lower for keyword in ranking_keywords):
        return "RANKING"
    
    # 3. TREND - Growth/Change over time
    trend_keywords = [
        "growth", "trend", "change", "increase", "decrease",
        "growing", "declining", "rising", "falling",
        "compared to last", "year over year", "yoy", "mom"
    ]
    if any(keyword in query_lower for keyword in trend_keywords):
        return "TREND"
    
    # 4. AGGREGATE - Sum/Average over period
    aggregate_keywords = [
        "past", "last", "total", "sum", "average", "mean",
        "year summary", "quarter total", "monthly average"
    ]
    # Check if it's asking for aggregation over multiple periods
    if any(keyword in query_lower for keyword in aggregate_keywords):
        # But not if it's a single specific period
        single_period_patterns = [
            r"sales on \d{4}-\d{2}-\d{2}",  # Specific date
            r"sales in (january|february|march|april|may|june|july|august|september|october|november|december) \d{4}",  # Specific month
        ]
        if not any(re.search(pattern, query_lower) for pattern in single_period_patterns):
            return "AGGREGATE"
    
    # 5. SINGLE_POINT - One specific value (default)
    return "SINGLE_POINT"


def get_intent_description(intent: IntentType) -> str:
    """Get human-readable description of intent type."""
    descriptions = {
        "SINGLE_POINT": "Retrieve a single specific value",
        "AGGREGATE": "Aggregate data over a period",
        "COMPARISON": "Compare two entities or periods",
        "RANKING": "Find highest or lowest performer",
        "TREND": "Analyze growth or change over time"
    }
    return descriptions.get(intent, "Unknown intent")


# Example usage and tests
if __name__ == "__main__":
    test_queries = [
        ("Today sales", "SINGLE_POINT"),
        ("June 2025 sales", "SINGLE_POINT"),
        ("Past 3 months", "AGGREGATE"),
        ("Year total 2025", "AGGREGATE"),
        ("Compare Branch 1 and Branch 2", "COMPARISON"),
        ("Branch 1 vs Branch 2", "COMPARISON"),
        ("Highest performing branch", "RANKING"),
        ("Which branch has lowest sales", "RANKING"),
        ("Sales growth this year", "TREND"),
        ("Trend for past 6 months", "TREND"),
    ]
    
    print("Intent Classification Tests:")
    print("-" * 60)
    for query, expected in test_queries:
        result = classify_intent(query)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{query}' → {result} (expected: {expected})")
