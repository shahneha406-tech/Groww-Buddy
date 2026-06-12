import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const chatBottomRef = useRef(null);

  // Auto-scroll to bottom of chat when a message is added or loading states change
  useEffect(() => {
    if (chatBottomRef.current) {
      chatBottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading]);

  const predefinedQueries = [
    "What is the exit load for HDFC Top 100?",
    "Who manages HDFC Mid-Cap Opportunities Fund?",
    "Current expense ratio of HDFC Small Cap Fund?",
    "Should I invest in HDFC Defence Fund?",
    "Top 5 holdings of HDFC Defence Fund?"
  ];

  const handleQuerySubmit = async (text) => {
    if (!text.trim()) return;

    // Add User Message
    const userMsg = { sender: 'user', text: text };
    setMessages(prev => [...prev, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text })
      });

      if (!response.ok) {
        throw new Error('API server returned an error');
      }

      const data = await response.json();
      const answer = data.response || "I cannot find this information in the official documents.";

      // Add Buddy Message
      setMessages(prev => [...prev, { sender: 'buddy', text: answer }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { 
        sender: 'buddy', 
        text: "Error connecting to the Groww Buddy API server. Please make sure the backend server python -m retrieval.api_server is running on port 8000." 
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Helper to parse responses into text, citation, and update date
  const parseResponse = (rawText) => {
    let text = rawText;
    let citation = "";
    let lastUpdated = "";

    // Extract Last updated timestamp
    const updatedMatch = text.match(/Last updated from sources:\s*(.*)/i);
    if (updatedMatch) {
      lastUpdated = updatedMatch[1].trim();
      text = text.replace(/Last updated from sources:\s*.*/i, "");
    }

    // Extract Source URL
    const sourceMatch = text.match(/Source:\s*(.*)/i);
    if (sourceMatch) {
      citation = sourceMatch[1].trim();
      text = text.replace(/Source:\s*.*/i, "");
    }

    return {
      text: text.trim(),
      citation: citation,
      lastUpdated: lastUpdated
    };
  };

  // Determine card type based on response content
  const getResponseType = (text) => {
    const textLower = text.toLowerCase();
    if (textLower.includes("personal identifier information") || textLower.includes("pii")) {
      return "pii_warning";
    }
    if (textLower.includes("cannot provide investment recommendations") || textLower.includes("advisory") || textLower.includes("sebi-registered")) {
      return "advisory_refusal";
    }
    if (textLower.includes("outside this domain") || textLower.includes("out-of-scope") || textLower.includes("outside the supported domain")) {
      return "out_of_scope";
    }
    if (textLower.includes("error connecting") || textLower.includes("error generating")) {
      return "error";
    }
    return "factual";
  };

  const isChatState = messages.length > 0;

  return (
    <div className="app-container">
      {/* Decorative Glow Spots */}
      <div className="bg-decorative-glow">
        <div className="glow-spot-1"></div>
        <div className="glow-spot-2"></div>
      </div>

      {/* Top Header Bar */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo-area">
            <div className="logo-group">
              <div className="logo-icon">
                <span className="material-symbols-outlined">trending_up</span>
              </div>
              <span>Groww Buddy</span>
            </div>
            <div className="logo-subtext">
              <span className="material-symbols-outlined subtext-warn-icon">warning</span>
              <span>Facts-only. No investment advice.</span>
            </div>
          </div>
          <div className="header-actions">
            <span className="material-symbols-outlined">notifications</span>
            <span className="material-symbols-outlined">account_circle</span>
          </div>
        </div>
      </header>

      {/* 3. Main Dashboard Area */}
      <main className="main-content">
        {!isChatState ? (
          // Landing View
          <div className="welcome-container">
            <div className="welcome-card">
              <div className="welcome-robot-icon">
                <span className="material-symbols-outlined">smart_toy</span>
              </div>
              <h1 className="welcome-title">Mutual Fund FAQ Assistant</h1>
              <p className="welcome-subtitle">
                Get verified, facts-only responses for HDFC mutual fund details.
              </p>
            </div>

            {/* Central Search Box */}
            <div className="search-wrapper">
              <div className="search-bar-container">
                <span className="material-symbols-outlined" style={{ color: '#85948c' }}>search</span>
                <input
                  type="text"
                  className="search-input-field"
                  placeholder="Ask about exit loads, holdings, or manager history..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleQuerySubmit(query);
                  }}
                />
                <button 
                  className="search-submit-btn"
                  onClick={() => handleQuerySubmit(query)}
                >
                  <span>Ask Buddy</span>
                  <span className="material-symbols-outlined">arrow_forward</span>
                </button>
              </div>
            </div>

            {/* Clickable Quick Pills */}
            <div className="shortcut-pills-container">
              {predefinedQueries.map((q, idx) => (
                <button
                  key={idx}
                  className="shortcut-pill-btn"
                  onClick={() => handleQuerySubmit(q)}
                >
                  {q}
                </button>
              ))}
            </div>

            {/* Bento-style Feature descriptions */}
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon-box">
                  <span className="material-symbols-outlined">verified_user</span>
                </div>
                <div>
                  <h3 className="feature-title">Verified Sources</h3>
                  <p className="feature-desc">All responses map directly back to official AMC fact sheets.</p>
                </div>
              </div>
              <div className="feature-card">
                <div className="feature-icon-box">
                  <span className="material-symbols-outlined">bolt</span>
                </div>
                <div>
                  <h3 className="feature-title">Instant Retrieval</h3>
                  <p className="feature-desc">Optimized local FAISS lookup engine ensures zero-latency search.</p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          // Active Chat View
          <div className="chat-container">
            {messages.map((msg, idx) => {
              if (msg.sender === 'user') {
                return (
                  <div key={idx} className="message-row user">
                    <div className="user-bubble">
                      <p>{msg.text}</p>
                    </div>
                  </div>
                );
              } else {
                const parsed = parseResponse(msg.text);
                const respType = getResponseType(parsed.text);

                if (respType === 'advisory_refusal') {
                  return (
                    <div key={idx} className="message-row buddy">
                      <div className="advisory-alert-card">
                        <span className="material-symbols-outlined advisory-icon">gavel</span>
                        <div>
                          <h3 className="advisory-title">Advisory Restriction</h3>
                          <p className="advisory-text">{parsed.text}</p>
                          <div className="advisory-links-row">
                            <a 
                              href="https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doInvestorEducation=yes" 
                              target="_blank" 
                              rel="noreferrer" 
                              className="advisory-link-btn"
                            >
                              <span>Visit SEBI Investor Education</span>
                              <span className="material-symbols-outlined">open_in_new</span>
                            </a>
                            <a 
                              href="https://www.amfiindia.com/" 
                              target="_blank" 
                              rel="noreferrer" 
                              className="advisory-link-btn"
                            >
                              <span>Visit AMFI India</span>
                              <span className="material-symbols-outlined">open_in_new</span>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                } else if (respType === 'out_of_scope') {
                  return (
                    <div key={idx} className="message-row buddy">
                      <div className="out-of-scope-card">
                        <span className="material-symbols-outlined out-of-scope-icon">info</span>
                        <div>
                          <h3 className="out-of-scope-title" style={{ color: '#ffc107' }}>Out of Scope</h3>
                          <p className="out-of-scope-text">{parsed.text}</p>
                        </div>
                      </div>
                    </div>
                  );
                } else if (respType === 'pii_warning') {
                  return (
                    <div key={idx} className="message-row buddy">
                      <div className="advisory-alert-card" style={{ border: '1px solid rgba(239, 68, 68, 0.4)' }}>
                        <span className="material-symbols-outlined" style={{ color: '#ef4444' }}>security</span>
                        <div>
                          <h3 className="advisory-title" style={{ color: '#ef4444' }}>Privacy Violation Blocked</h3>
                          <p className="advisory-text">{parsed.text}</p>
                        </div>
                      </div>
                    </div>
                  );
                } else if (respType === 'error') {
                  return (
                    <div key={idx} className="message-row buddy">
                      <div className="advisory-alert-card" style={{ border: '1px solid rgba(239, 68, 68, 0.4)' }}>
                        <span className="material-symbols-outlined" style={{ color: '#ef4444' }}>error</span>
                        <div>
                          <h3 className="advisory-title" style={{ color: '#ef4444' }}>System Error</h3>
                          <p className="advisory-text">{parsed.text}</p>
                        </div>
                      </div>
                    </div>
                  );
                } else {
                  return (
                    <div key={idx} className="message-row buddy">
                      <div className="buddy-card">
                        <div className="buddy-badge-row">
                          <div className="buddy-badge-icon">
                            <span className="material-symbols-outlined">auto_awesome</span>
                          </div>
                          <span className="buddy-badge-text">Verified Response</span>
                        </div>
                        <p className="buddy-text">{parsed.text}</p>
                        <div className="buddy-citation-row">
                          {parsed.citation && (
                            <a 
                              href={parsed.citation} 
                              target="_blank" 
                              rel="noreferrer" 
                              className="citation-chip"
                            >
                              <span className="material-symbols-outlined">link</span>
                              <span>Source fact sheet</span>
                            </a>
                          )}
                          {parsed.lastUpdated && (
                            <span className="updated-timestamp">
                              Last updated from sources: {parsed.lastUpdated}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                }
              }
            })}

            {/* Bouncing Dots Loader Bubble */}
            {loading && (
              <div className="message-row buddy">
                <div className="buddy-card" style={{ padding: '16px 24px', maxWidth: '160px' }}>
                  <div className="buddy-loader">
                    <div className="loader-dot"></div>
                    <div className="loader-dot"></div>
                    <div className="loader-dot"></div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Scroll Anchor */}
            <div ref={chatBottomRef} />
          </div>
        )}
      </main>

      {/* 4. Bottom Fixed Input Dock (Visible when Chat history is active) */}
      {isChatState && (
        <div className="input-dock-container">
          <div className="input-dock-content">
            <div className="input-dock-search-box">
              <span className="material-symbols-outlined input-dock-search-icon">search</span>
              <input
                type="text"
                className="input-dock-field"
                placeholder="Ask another question about mutual funds..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleQuerySubmit(query);
                }}
                disabled={loading}
              />
              <button 
                className="input-send-btn"
                onClick={() => handleQuerySubmit(query)}
                disabled={loading}
              >
                <span className="material-symbols-outlined">send</span>
              </button>
            </div>
            <div className="dock-actions-row">
              <button className="dock-action-btn" onClick={() => setMessages([])}>
                <span className="material-symbols-outlined">restart_alt</span>
                <span>Reset Chat</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 5. Static Risk Disclaimer Footer */}
      {!isChatState && (
        <footer className="app-footer">
          <div className="footer-disclaimer">
            Mutual fund investments are subject to market risks. Read all scheme related documents carefully before investing. 
            Groww Buddy provides factual information only and does not constitute financial, investment, or tax advice.
          </div>
          <div className="footer-links">
            <a href="https://groww.in/pages/privacy-policy" target="_blank" rel="noreferrer">Privacy Policy</a>
            <a href="https://groww.in/pages/terms-and-conditions" target="_blank" rel="noreferrer">Terms and conditions</a>
            <a href="https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doInvestorEducation=yes" target="_blank" rel="noreferrer">SEBI Education</a>
          </div>
        </footer>
      )}
    </div>
  );
}

export default App;
