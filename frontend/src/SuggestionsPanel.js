
import React from "react";
import "./SuggestionsPanel.css";

function SuggestionsPanel({ onSelect, userRole }) {
    // Enterprise UX: Quick Insights - Predefined Safe Queries
    const allInsights = [
        { query: "Sales of Branch 1 today", allowedRoles: ["STAFF", "MANAGER", "ADMIN", "OWNER"] },
        { query: "Which branch has highest sales this month?", allowedRoles: ["MANAGER", "ADMIN", "OWNER"] },
        { query: "Lowest performing branch this year", allowedRoles: ["MANAGER", "ADMIN", "OWNER"] },
        { query: "Past 3 months sales summary", allowedRoles: ["STAFF", "MANAGER", "ADMIN", "OWNER"] },
        { query: "Compare Branch 1 and Branch 2", allowedRoles: ["MANAGER", "ADMIN", "OWNER"] }
    ];

    // Filter insights based on user role
    const quickInsights = allInsights
        .filter(insight => insight.allowedRoles.includes(userRole))
        .map(insight => insight.query);

    return (
        <div className="suggestions-panel">
            <div className="suggestion-group">
                <div className="group-title">Quick Insights</div>
                <div className="chips-container">
                    {quickInsights.map((query, idx) => (
                        <div
                            key={idx}
                            className="suggestion-chip insight-chip"
                            onClick={() => onSelect(query)}
                        >
                            {query}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default SuggestionsPanel;
