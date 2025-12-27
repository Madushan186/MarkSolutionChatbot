
import React, { useEffect, useState } from "react";
import axios from "axios";
import "./SuggestionsPanel.css";

function SuggestionsPanel({ onSelect }) {
    const [suggestions, setSuggestions] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSuggestions = async () => {
            try {
                const res = await axios.get("http://127.0.0.1:8000/suggestions");
                setSuggestions(res.data);
            } catch (err) {
                console.error("Failed to load suggestions", err);
            } finally {
                setLoading(false);
            }
        };
        fetchSuggestions();
    }, []);

    if (loading) return null; // Or a small skeleton loader
    if (!suggestions) return null;

    return (
        <div className="suggestions-panel">
            {Object.entries(suggestions).map(([category, items]) => (
                <div key={category} className="suggestion-group">
                    <div className="group-title">{category}</div>
                    <div className="chips-container">
                        {items.map((item, idx) => (
                            <div
                                key={idx}
                                className="suggestion-chip"
                                onClick={() => onSelect(item)}
                            >
                                {item}
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
}

export default SuggestionsPanel;
