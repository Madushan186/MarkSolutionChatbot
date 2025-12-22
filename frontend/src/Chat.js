import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./Chat.css";

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

function Chat() {
    const [messages, setMessages] = useState([
        { sender: "bot", text: "Welcome to MarkSolution Enterprise.\nI am ready to analyze your daily reports and financial data." }
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([]);
    const messagesEndRef = useRef(null);

    // Fetch Suggestions
    useEffect(() => {
        const fetchSuggestions = async () => {
            if (input.length < 2) {
                setSuggestions([]);
                return;
            }
            try {
                const res = await axios.post("http://127.0.0.1:8000/suggest", { input });
                setSuggestions(res.data.suggestions);
            } catch (err) {
                console.error("Suggestion Error", err);
            }
        };

        // Debounce slightly to avoid rapid calls
        const timer = setTimeout(() => {
            fetchSuggestions();
        }, 300);

        return () => clearTimeout(timer);
    }, [input]);

    const handleSuggestionClick = (text) => {
        setInput(text);
        setSuggestions([]);
        // Optional: Auto-focus back to input
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;
        const userMsg = input.trim();
        const newMessages = [...messages, { sender: "user", text: userMsg }];
        setMessages(newMessages);
        setInput("");
        setIsLoading(true);

        try {
            const res = await axios.post("http://127.0.0.1:8000/chat", {
                message: userMsg
            });
            const botResponse = res.data && res.data.answer ? res.data.answer : "System Error: Invalid response format.";
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
                    <div className="brand-icon">MS</div>
                    <span>MarkSolution</span>
                </div>

                <div className="nav-menu">
                    <div className="nav-item">
                        <IconDashboard /> Dashboard
                    </div>
                    <div className="nav-item active">
                        <IconChat /> AI Assistant
                    </div>
                    <div className="nav-item">
                        <IconAnalytics /> Analytics
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="chat-main">
                <div className="chat-header-minimal">
                    <div className="header-title">Enterprise Assistant v1.0</div>
                    <div className="status-badge">Online</div>
                </div>

                <div className="chat-window">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`message-row ${msg.sender}`}>
                            {msg.sender === "bot" && (
                                <div className="avatar bot-icon">AI</div>
                            )}

                            <div className="message-bubble">
                                {msg.text}
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

                <div className="input-area">
                    <div className="input-pill">
                        <input
                            className="chat-input"
                            placeholder="Ask about financial reports..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                        />
                        <button
                            className={`send-btn ${input.trim() ? "ready" : ""}`}
                            onClick={sendMessage}
                            disabled={!input.trim()}
                        >
                            <IconSend />
                        </button>
                    </div>

                    {/* Suggestions List */}
                    {suggestions.length > 0 && (
                        <div className="suggestion-box">
                            {suggestions.map((s, idx) => (
                                <div
                                    key={idx}
                                    className="suggestion-item"
                                    onClick={() => handleSuggestionClick(s)}
                                >
                                    {s}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Chat;
