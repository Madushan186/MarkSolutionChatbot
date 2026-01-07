import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./Chat.css";
import SuggestionsPanel from "./SuggestionsPanel";
import msLogo from './mark_solution_logo.png';

// Mock Icons (Simple SVG paths)
const IconDashboard = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" class="icon" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /></svg>
);
const IconChat = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" class="icon" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
);
const IconAnalytics = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" class="icon" stroke="currentColor" strokeWidth="2"><path d="M18 20V10" /><path d="M12 20V4" /><path d="M6 20v-6" /></svg>
);
const IconSend = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" /></svg>
);
const IconCopy = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
);
const IconCheck = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
);
const IconStar = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
);
const IconPlay = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
);
const IconTrash = () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
);
const IconLogout = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" class="icon" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
);

function Chat({ user, onLogout }) {
    const [messages, setMessages] = useState([
        { sender: "bot", text: `Welcome back, ${user.name}. I am ready to analyze your financial data.` }
    ]);
    const [input, setInput] = useState("");
    const [showMenu, setShowMenu] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [copiedIndex, setCopiedIndex] = useState(null);
    const [copiedCodeBlock, setCopiedCodeBlock] = useState(null);
    const [savedQueries, setSavedQueries] = useState([]);
    const [lastResolvedQuery, setLastResolvedQuery] = useState(null);
    const messagesEndRef = useRef(null);

    // Enterprise UX: Rotating Placeholder
    const placeholders = [
        "Try: Today sales",
        "Try: Past 3 months",
        "Try: Branch 1 this month",
        "Try: Compare Branch 1 & 2"
    ];
    const [placeholderIndex, setPlaceholderIndex] = useState(0);

    // Enterprise UX: Smart Dropdowns (Query Builder)
    const [selectedMetric, setSelectedMetric] = useState("");
    const [selectedPeriod, setSelectedPeriod] = useState("");
    const [selectedBranch, setSelectedBranch] = useState("");
    const [showQueryBuilder, setShowQueryBuilder] = useState(false);

    // Enterprise UX: Error Prevention
    const [showAlternatives, setShowAlternatives] = useState(false);

    // Enterprise UX: Role-Based UI Visibility
    const isStaff = user.role === "STAFF";
    const canCompare = ["ADMIN", "OWNER", "MANAGER"].includes(user.role);

    // Load saved queries on mount
    useEffect(() => {
        const saved = localStorage.getItem("mark_saved_queries");
        if (saved) {
            setSavedQueries(JSON.parse(saved));
        }
    }, []);

    // Save Logic
    const saveQuery = (queryText, label) => {
        const newQuery = {
            id: Date.now(),
            label: label || queryText,
            query: queryText
        };
        const updated = [...savedQueries, newQuery];
        setSavedQueries(updated);
        localStorage.setItem("mark_saved_queries", JSON.stringify(updated));
    };

    const deleteQuery = (id) => {
        const updated = savedQueries.filter(q => q.id !== id);
        setSavedQueries(updated);
        localStorage.setItem("mark_saved_queries", JSON.stringify(updated));
    };

    // Run Saved Query
    const runSavedQuery = (queryText) => {
        setInput(queryText);
        sendMessage(queryText);
    };

    const handleSuggestionClick = (text) => {
        setInput(text);
    };

    // Enterprise UX: Quick Action Handler (Auto-Submit)
    const handleQuickAction = (query) => {
        setInput(query);
        sendMessage(query);
    };

    // Enterprise UX: Auto-Compose Query from Dropdowns
    const composeAndSubmitQuery = () => {
        if (!selectedMetric || !selectedPeriod || !selectedBranch) {
            return; // Need all three selections
        }

        // Compose query: "Average sales for Branch 1 in past 3 months"
        const query = `${selectedMetric} for ${selectedBranch} in ${selectedPeriod}`;

        // Reset selections
        setSelectedMetric("");
        setSelectedPeriod("");
        setSelectedBranch("");
        setShowQueryBuilder(false);

        // Submit
        setInput(query);
        sendMessage(query);
    };

    // Enterprise UX: Detect Unsupported Queries
    const detectUnsupportedQuery = (text) => {
        const unsupportedKeywords = ["why", "what caused", "reason for", "reason behind", "explain why", "cause of"];
        return unsupportedKeywords.some(keyword => text.toLowerCase().includes(keyword));
    };

    // Handle input change with error prevention
    const handleInputChange = (e) => {
        const value = e.target.value;
        setInput(value);

        // Show alternatives if unsupported query detected
        if (value.trim() && detectUnsupportedQuery(value)) {
            setShowAlternatives(true);
        } else {
            setShowAlternatives(false);
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    // Enterprise UX: Rotate Placeholder every 3 seconds
    useEffect(() => {
        const interval = setInterval(() => {
            setPlaceholderIndex((prev) => (prev + 1) % placeholders.length);
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleCopy = (text, index) => {
        navigator.clipboard.writeText(text).then(() => {
            setCopiedIndex(index);
            setTimeout(() => setCopiedIndex(null), 1500);
        });
    };

    const handleCodeBlockCopy = (code, blockId) => {
        navigator.clipboard.writeText(code).then(() => {
            setCopiedCodeBlock(blockId);
            setTimeout(() => setCopiedCodeBlock(null), 1500);
        });
    };

    // Format message with GPT-style code blocks
    const formatMessage = (text, msgIndex) => {
        const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
        const parts = [];
        let lastIndex = 0;
        let match;
        let blockCounter = 0;

        while ((match = codeBlockRegex.exec(text)) !== null) {
            // Add text before code block
            if (match.index > lastIndex) {
                parts.push({
                    type: 'text',
                    content: text.substring(lastIndex, match.index)
                });
            }

            // Add code block
            const lang = match[1] || 'code';
            const code = match[2].trim();
            const blockId = `${msgIndex}-${blockCounter}`;
            blockCounter++;

            parts.push({
                type: 'code',
                lang: lang,
                code: code,
                blockId: blockId
            });

            lastIndex = match.index + match[0].length;
        }

        // Add remaining text
        if (lastIndex < text.length) {
            parts.push({
                type: 'text',
                content: text.substring(lastIndex)
            });
        }

        // If no code blocks found, return text as is
        if (parts.length === 0) {
            return [{ type: 'text', content: text }];
        }

        return parts;
    };

    const sendMessage = async (overrideText = null) => {
        const textToSend = overrideText || input;

        if (!textToSend.trim() || isLoading) return;

        // NLU Interceptor: "Save as [Label]"
        const saveMatch = textToSend.match(/^save (?:as )?(.+)$/i);
        if (saveMatch) {
            if (lastResolvedQuery) {
                saveQuery(lastResolvedQuery, saveMatch[1]);
                setMessages(prev => [...prev, { sender: "bot", text: `✅ Saved query context: "${lastResolvedQuery}" as "${saveMatch[1]}"` }]);
            } else {
                setMessages(prev => [...prev, { sender: "bot", text: `⚠️ No active query context to save. Run a query first.` }]);
            }
            setInput("");
            return;
        }

        const userMsg = textToSend.trim();
        const newMessages = [...messages, { sender: "user", text: userMsg }];
        setMessages(newMessages);
        if (!overrideText) setInput("");
        setIsLoading(true);
        setCopiedIndex(null);

        try {
            const res = await axios.post("http://127.0.0.1:8000/chat", {
                message: userMsg,
                role: user.role,
                branch_id: user.branch
            });
            const botResponse = res.data && res.data.answer ? res.data.answer : "System Error: Invalid response format.";
            const resolvedCtx = res.data && res.data.resolved_query ? res.data.resolved_query : userMsg;
            setLastResolvedQuery(resolvedCtx);

            setMessages(prev => [...prev, { sender: "bot", text: botResponse }]);
        } catch (err) {
            console.error(err);
            setMessages(prev => [...prev, { sender: "bot", text: "Connection error. Please check system status." }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="app-layout">
            {/* Dark Glass Sidebar */}
            <div className="sidebar">
                <div className="sidebar-header">
                    <img src={msLogo} alt="MarkSolution Logo" className="brand-logo" />
                    <span>MarkSolution</span>
                </div>

                <div className="nav-menu">
                    {/* Role Badge */}
                    <div className="user-profile">
                        <div className="user-avatar">{user.name[0].toUpperCase()}</div>
                        <div className="user-info">
                            <div className="user-name">{user.name}</div>
                            <div className="user-role">{user.role.replace('_', ' ')} {user.branch !== 'ALL' && `(Br: ${user.branch})`}</div>
                        </div>
                    </div>

                    <div className="nav-item">
                        <IconDashboard /> Dashboard
                    </div>
                    <div className="nav-item active">
                        <IconChat /> AI Assistant
                    </div>
                    <div className="nav-item">
                        <IconAnalytics /> Analytics
                    </div>

                    {/* Saved Queries Section */}
                    {savedQueries.length > 0 && (
                        <div className="saved-queries-section">
                            <div className="section-label">SAVED SHORTCUTS</div>
                            <div className="saved-list">
                                {savedQueries.map(q => (
                                    <div key={q.id} className="saved-item" onClick={() => runSavedQuery(q.query)}>
                                        <div className="saved-icon"><IconPlay /></div>
                                        <span className="saved-label">{q.label}</span>
                                        <div className="delete-btn" onClick={(e) => { e.stopPropagation(); deleteQuery(q.id); }}>
                                            <IconTrash />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="nav-spacer"></div>

                    <div className="nav-item logout-btn" onClick={onLogout}>
                        <IconLogout /> Logout
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="chat-main">
                <div className="chat-header-minimal">
                    <div className="header-title">Enterprise Assistant v2.0</div>
                    <div className="status-badge">Online</div>
                </div>

                <div className="chat-window">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`message-row ${msg.sender}`}>
                            {msg.sender === "bot" && (
                                <div className="avatar bot-icon">AI</div>
                            )}

                            <div className="message-bubble">
                                {formatMessage(msg.text, idx).map((part, partIdx) => (
                                    <React.Fragment key={partIdx}>
                                        {part.type === 'text' ? (
                                            <span dangerouslySetInnerHTML={{ __html: part.content }} />
                                        ) : (
                                            <div className="gpt-codeblock">
                                                <div className="gpt-header">
                                                    <span className="lang">{part.lang}</span>
                                                    <button
                                                        className="copy-btn-code"
                                                        onClick={() => handleCodeBlockCopy(part.code, part.blockId)}
                                                    >
                                                        {copiedCodeBlock === part.blockId ? 'Copied!' : 'Copy code'}
                                                    </button>
                                                </div>
                                                <pre><code>{part.code}</code></pre>
                                            </div>
                                        )}
                                    </React.Fragment>
                                ))}
                                <button
                                    className={`copy-btn ${copiedIndex === idx ? "copied" : ""}`}
                                    onClick={() => handleCopy(msg.text, idx)}
                                    title="Copy to clipboard"
                                >
                                    {copiedIndex === idx ? <IconCheck /> : <IconCopy />}
                                </button>
                                {/* Save Context Button for User Messages */}
                                {msg.sender === "user" && idx > 0 && (
                                    <button
                                        className="save-ctx-btn"
                                        onClick={() => {
                                            saveQuery(msg.text, `Query ${savedQueries.length + 1}`);
                                        }}
                                        title="Save this query"
                                    >
                                        <IconStar />
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="message-row bot">
                            <div className="avatar bot-icon">AI</div>
                            <div className="message-bubble loading-bubble">
                                <div className="typing-dots">
                                    <span></span><span></span><span></span>
                                </div>
                                <span className="loading-text">Analyzing securely...</span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Smart Suggestions Panel */}
                <div className="suggestion-wrapper">
                    <SuggestionsPanel onSelect={handleQuickAction} userRole={user.role} />
                </div>

                {/* STICKY BOTTOM QUERY BAR (Unified Layout) */}
                {/* ChatGPT-Style Centered Input Area */}
                <div className="chat-input-area">
                    {/* Enterprise UX: Smart Dropdowns (Query Builder) */}
                    <div className="query-builder-container">
                        <button
                            className="query-builder-toggle"
                            onClick={() => setShowQueryBuilder(!showQueryBuilder)}
                        >
                            {showQueryBuilder ? "Hide" : "Build"} Query
                        </button>

                        {showQueryBuilder && (
                            <div className="query-builder">
                                <div className="builder-row">
                                    <div className="dropdown-group">
                                        <label>Metric</label>
                                        <select
                                            value={selectedMetric}
                                            onChange={(e) => setSelectedMetric(e.target.value)}
                                            className="builder-select"
                                        >
                                            <option value="">Select...</option>
                                            <option value="Total sales">Total Sales</option>
                                            <option value="Average sales">Average Sales</option>
                                            <option value="Highest sales">Highest Sales</option>
                                            <option value="Lowest sales">Lowest Sales</option>
                                        </select>
                                    </div>

                                    <div className="dropdown-group">
                                        <label>Period</label>
                                        <select
                                            value={selectedPeriod}
                                            onChange={(e) => setSelectedPeriod(e.target.value)}
                                            className="builder-select"
                                        >
                                            <option value="">Select...</option>
                                            <option value="today">Today</option>
                                            <option value="yesterday">Yesterday</option>
                                            <option value="this month">This Month</option>
                                            <option value="last month">Last Month</option>
                                            <option value="past 3 months">Past 3 Months</option>
                                            <option value="past 6 months">Past 6 Months</option>
                                            <option value="this year">This Year</option>
                                        </select>
                                    </div>

                                    <div className="dropdown-group">
                                        <label>Branch</label>
                                        <select
                                            value={selectedBranch}
                                            onChange={(e) => setSelectedBranch(e.target.value)}
                                            className="builder-select"
                                        >
                                            <option value="">Select...</option>
                                            <option value="All Branches">All Branches</option>
                                            <option value="Branch 1">Branch 1</option>
                                            <option value="Branch 2">Branch 2</option>
                                            <option value="Branch 3">Branch 3</option>
                                        </select>
                                    </div>

                                    <button
                                        className="builder-submit-btn"
                                        onClick={composeAndSubmitQuery}
                                        disabled={!selectedMetric || !selectedPeriod || !selectedBranch}
                                    >
                                        Submit
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Enterprise UX: Quick Action Buttons (Always Visible Above Input) */}
                    <div className="quick-action-buttons">
                        {[
                            { label: "Today", query: "Today sales" },
                            { label: "Yesterday", query: "Yesterday sales" },
                            { label: "This Month", query: "This month sales" },
                            { label: "Past 3 Months", query: "Past 3 months" },
                            { label: "This Year", query: "This year sales" }
                        ].map(action => (
                            <button
                                key={action.label}
                                className="quick-action-btn"
                                onClick={() => handleQuickAction(action.query)}
                            >
                                {action.label}
                            </button>
                        ))}
                    </div>


                    <div className="input-container">
                        {/* Menu Toggle */}
                        <div className="menu-wrapper">
                            <button
                                className={`attach-btn ${showMenu ? "active" : ""}`}
                                onClick={() => setShowMenu(!showMenu)}
                            >
                                <span className="plus-icon">+</span>
                            </button>

                            {/* Dropdown Menu */}
                            {showMenu && (
                                <div className="input-dropdown">
                                    <div className="dropdown-section">
                                        <div className="dropdown-label">METRICS</div>
                                        <div className="dropdown-grid">
                                            {["Total", "Average", "Count", "Min", "Max"].map(m => (
                                                <div
                                                    key={m}
                                                    className="dropdown-item"
                                                    onClick={() => {
                                                        setInput(prev => prev + (prev ? " " : "") + m);
                                                        setShowMenu(false);
                                                    }}
                                                >
                                                    {m}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                    <div className="dropdown-divider"></div>
                                    <div className="dropdown-section">
                                        <div className="dropdown-label">SHORTCUTS</div>
                                        {["Past 3 months sales", "past year sales", "this month sales", "past 6 month sale"].map(s => (
                                            <div
                                                key={s}
                                                className="dropdown-item row-item"
                                                onClick={() => {
                                                    setInput(prev => prev + (prev ? " " : "") + s);
                                                    setShowMenu(false);
                                                }}
                                            >
                                                {s}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        <input
                            className="chat-input-field"
                            placeholder={placeholders[placeholderIndex]}
                            value={input}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            autoFocus
                        />

                        {/* Enterprise UX: Error Prevention - Alternative Suggestions */}
                        {showAlternatives && (
                            <div className="query-alternatives">
                                <div className="alternatives-title">Try these instead:</div>
                                <button
                                    className="alternative-btn"
                                    onClick={() => {
                                        setInput("Compare this month vs last month");
                                        setShowAlternatives(false);
                                    }}
                                >
                                    Compare this month vs last month
                                </button>
                                <button
                                    className="alternative-btn"
                                    onClick={() => {
                                        setInput("Past 3 months sales");
                                        setShowAlternatives(false);
                                    }}
                                >
                                    Show sales trend
                                </button>
                                <button
                                    className="alternative-btn"
                                    onClick={() => {
                                        setInput("Compare Branch 1 and Branch 2");
                                        setShowAlternatives(false);
                                    }}
                                >
                                    View branch comparison
                                </button>
                            </div>
                        )}

                        <button
                            className={`send-action-btn ${input.trim() ? "ready" : ""}`}
                            onClick={() => sendMessage()}
                            disabled={!input.trim()}
                        >
                            <IconSend />
                        </button>
                    </div>
                    <div className="input-footer">
                        Mr. Mark Assistant can make mistakes. Please verify important info.
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Chat;