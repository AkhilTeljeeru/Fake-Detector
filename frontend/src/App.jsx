import React, { useState } from 'react';
import './index.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('manual'); // 'manual' | 'search'
  
  // Manual Input State
  const [text, setText] = useState('');
  
  // Search State
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  
  // Global State
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePredictManual = async (type) => {
    if (!text.trim()) {
      setError('Please enter some text to analyze.');
      return;
    }
    
    setError('');
    setLoading(true);
    setResult(null);

    const endpoint = type === 'news' ? '/predict-news' : '/predict-phishing';
    
    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      
      let isDanger = false;
      if (data.prediction === 'Fake News' || data.prediction === 'Phishing') {
        isDanger = true;
      }
      
      setResult({
        ...data,
        isDanger,
        type
      });
    } catch (err) {
      setError(err.message || 'Something went wrong. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchWeb = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a topic to search.');
      return;
    }
    
    setError('');
    setLoading(true);
    setSearchResults([]);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/search-web`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (err) {
      setError(err.message || 'Something went wrong during search.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeUrl = async (url) => {
    setError('');
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/analyze-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `API error: ${response.statusText}`);
      }

      const data = await response.json();
      
      let isDanger = false;
      if (data.prediction === 'Fake News' || data.prediction === 'Phishing') {
        isDanger = true;
      }
      
      setResult({
        ...data,
        isDanger,
        type: 'news'
      });
    } catch (err) {
      setError(err.message || 'Something went wrong analyzing the URL.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{maxWidth: '850px'}}>
      <header className="header">
        <h1>🛡️ AI Fake News & Phishing Detector</h1>
        <p>Detect misinformation & cyber threats instantly using advanced NLP.</p>
        
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'manual' ? 'active' : ''}`}
            onClick={() => { setActiveTab('manual'); setResult(null); setError(''); }}
          >
            ✍️ Manual Text
          </button>
          <button 
            className={`tab ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => { setActiveTab('search'); setResult(null); setError(''); }}
          >
            🌐 Search Web (Live URLs)
          </button>
        </div>
      </header>
      
      <main className="main-content">
        {error && <div className="error-message">⚠️ {error}</div>}

        {activeTab === 'manual' ? (
          <div className="tab-pane fadeIn">
            <textarea
              className="input-textarea"
              placeholder="Paste news article or email content here..."
              value={text}
              onChange={(e) => {
                setText(e.target.value);
                if (error) setError('');
              }}
              disabled={loading}
            />
            
            <div className="button-group">
              <button 
                className="btn btn-primary" 
                onClick={() => handlePredictManual('news')}
                disabled={loading}
              >
                📰 Check Fake News
              </button>
              <button 
                className="btn btn-secondary" 
                onClick={() => handlePredictManual('phishing')}
                disabled={loading}
              >
                📧 Check Phishing
              </button>
            </div>
          </div>
        ) : (
          <div className="tab-pane fadeIn">
            <div className="search-bar-row">
              <input 
                type="text" 
                className="input-text"
                placeholder="Search topic (e.g. Technology, Apple, Politics)..."
                value={searchQuery}
                onKeyDown={(e) => e.key === 'Enter' && handleSearchWeb()}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  if (error) setError('');
                }}
                disabled={loading}
              />
              <button 
                className="btn btn-primary"
                style={{flex: '0 0 auto', padding: '0.75rem 2rem'}}
                onClick={handleSearchWeb}
                disabled={loading}
              >
                🔍 Search
              </button>
            </div>

            {searchResults.length > 0 && !result && (
              <div className="search-results">
                <h3>Live Web Results</h3>
                <p style={{marginBottom: '1rem', color: '#9ca3af', fontSize: '0.9rem'}}>Click on any article below to instantly analyze it.</p>
                <div className="results-list">
                  {searchResults.map((res, i) => (
                    <div key={i} className="search-card" onClick={() => handleAnalyzeUrl(res.href)}>
                      <h4>{res.title}</h4>
                      <p className="res-body">{res.body}</p>
                      <a href={res.href} target="_blank" rel="noreferrer" className="res-link" onClick={e => e.stopPropagation()}>{res.href.substring(0, 50)}...</a>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {loading && (
          <div className="loading-spinner fadeIn">
            <div className="spinner"></div>
            <p>Processing with AI models...</p>
          </div>
        )}

        {result && !loading && (
           <div className={`result-card ${result.isDanger ? 'danger' : 'safe'} fadeIn`}>
            <h2>Analysis Result</h2>
            <div className="result-label">
              Classification: <strong>{result.prediction}</strong>
            </div>
            <div className="confidence-score">
              Confidence Score: <strong>{(result.confidence * 100).toFixed(2)}%</strong>
            </div>

            {result.extracted_text && (
              <div className="extracted-text-preview">
                <h4 style={{marginTop: '1.5rem', marginBottom: '0.5rem', fontSize: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1rem'}}>Text Extracted from Source:</h4>
                <p style={{fontStyle: 'italic', opacity: 0.8, fontSize: '0.95rem', lineHeight: '1.5'}}>{result.extracted_text}</p>
              </div>
            )}
            
            {activeTab === 'search' && (
               <button className="btn btn-secondary" style={{marginTop: '1.5rem', width: 'fit-content'}} onClick={() => setResult(null)}>
                 ← Back to Results
               </button>
            )}
          </div>
        )}
      </main>
      
      <footer className="footer">
         Powered by FastAPI & Scikit-Learn | DuckDuckGo Web Search
      </footer>
    </div>
  );
}

export default App;
