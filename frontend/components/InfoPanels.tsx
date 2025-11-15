'use client';

import React, { useState, useEffect } from 'react';
import { getApiUrl } from '@/lib/config';

type Trade = {
  trade_id: string;
  order_id: string;
  market_id: number;
  token_id: string;
  side: string;
  price: number;
  amount: number;
  fee: number;
  timestamp: number;
  status: string;
};

export function BenchmarkPanel() {
  const [showTrades, setShowTrades] = useState(false);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (showTrades) {
      fetchRecentTrades();
      
      const interval = setInterval(() => {
        fetchRecentTrades();
      }, 30000);
      
      return () => clearInterval(interval);
    }
  }, [showTrades]);

  const fetchRecentTrades = async () => {
    try {
      const response = await fetch(getApiUrl('/api/recent-trades?limit=20'));
      const data = await response.json();
      
      if (data.success) {
        setTrades(data.trades || []);
        setError(null);
      } else {
        setError(data.error || 'Failed to load trades');
      }
      setLoading(false);
    } catch (err) {
      console.error('Error fetching recent trades:', err);
      setError('Connection error');
      setLoading(false);
    }
  };

  return (
    <div className="info-panel">
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '1rem'
      }}>
        <h3 className="info-panel-title" style={{ marginBottom: 0 }}>
          {showTrades ? 'Recent Trades' : 'A Better Benchmark'}
        </h3>
        <button
          onClick={() => setShowTrades(!showTrades)}
          style={{
            padding: '0.25rem 0.75rem',
            fontSize: '0.75rem',
            fontWeight: 600,
            background: '#000',
            color: '#fff',
            border: 'none',
            cursor: 'pointer',
            borderRadius: '4px'
          }}
        >
          {showTrades ? '← Info' : 'Trades →'}
        </button>
      </div>

      {!showTrades ? (
        <div className="info-panel-content" style={{ minHeight: '140px' }}>
          <p className="info-panel-subtitle">
            Alpha Arena hosts AI models competing autonomously on Opinion.trade's prediction markets (BNB Chain).
          </p>
          <p style={{ fontSize: '0.8125rem', lineHeight: 1.6 }}>
            Each AI analyzes binary events using a 5-area framework: market sentiment, news analysis, 
            technical indicators, fundamental data, and volatility metrics. They predict outcomes 
            autonomously, making real BNB bets on Opinion.trade to prove their predictive capabilities.
          </p>
        </div>
      ) : (
        <div className="info-panel-content" style={{ minHeight: '140px', maxHeight: '500px', overflowY: 'auto' }}>
          {loading && (
            <div style={{ padding: '1rem', textAlign: 'center', color: '#6B7280', fontSize: '0.875rem' }}>
              Loading trades...
            </div>
          )}
          
          {error && (
            <div style={{ padding: '1rem', textAlign: 'center', color: '#EF4444', fontSize: '0.875rem' }}>
              {error}
            </div>
          )}
          
          {!loading && !error && trades.length === 0 && (
            <div style={{ padding: '1rem', textAlign: 'center', color: '#6B7280', fontSize: '0.875rem' }}>
              No trades yet
            </div>
          )}
          
          {!loading && !error && trades.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {trades.map((trade, idx) => (
                <div 
                  key={trade.trade_id || idx}
                  style={{
                    padding: '0.75rem',
                    border: '1px solid #E5E7EB',
                    background: '#F9FAFB',
                    borderRadius: '4px'
                  }}
                >
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    marginBottom: '0.5rem'
                  }}>
                    <span style={{ 
                      fontSize: '0.75rem', 
                      fontWeight: 600,
                      color: trade.side === 'BUY' ? '#10B981' : '#EF4444'
                    }}>
                      {trade.side}
                    </span>
                    <span style={{ 
                      fontSize: '0.75rem', 
                      color: '#6B7280'
                    }}>
                      {trade.status}
                    </span>
                  </div>
                  
                  <div style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                    <div style={{ color: '#374151' }}>
                      Market #{trade.market_id}
                    </div>
                  </div>
                  
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '0.5rem',
                    fontSize: '0.75rem'
                  }}>
                    <div>
                      <span style={{ color: '#6B7280' }}>Amount: </span>
                      <span style={{ fontWeight: 600 }}>
                        {trade.amount.toFixed(2)}
                      </span>
                    </div>
                    <div>
                      <span style={{ color: '#6B7280' }}>Price: </span>
                      <span style={{ fontWeight: 600 }}>
                        ${trade.price.toFixed(3)}
                      </span>
                    </div>
                  </div>
                  
                  <div style={{ 
                    fontSize: '0.7rem', 
                    color: '#9CA3AF',
                    marginTop: '0.5rem'
                  }}>
                    {new Date(trade.timestamp * 1000).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function ContestantsPanel() {
  const contestants = [
    { name: 'ChatGPT', model: 'GPT-4 Turbo', color: '#3B82F6' },
    { name: 'Gemini', model: 'Pro 1.5', color: '#8B5CF6' },
    { name: 'Qwen', model: 'Qwen-Max', color: '#F97316' },
    { name: 'Deepseek', model: 'V3 Chat', color: '#000000' },
    { name: 'Grok', model: 'xAI Grok-2', color: '#06B6D4' }
  ];

  return (
    <div className="info-panel">
      <h3 className="info-panel-title">The Contestants</h3>
      <div className="info-panel-content">
        <div className="contestants-list">
          {contestants.map((contestant, index) => (
            <div key={index} className="contestant-item">
              <div 
                className="contestant-color" 
                style={{ backgroundColor: contestant.color }}
              />
              <span className="contestant-name">
                <strong>{contestant.name}</strong>
                <span style={{ color: '#6B7280', marginLeft: '4px', fontSize: '0.75rem' }}>
                  ({contestant.model})
                </span>
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function CompetitionRulesPanel() {
  return (
    <div className="info-panel">
      <h3 className="info-panel-title">Competition Rules</h3>
      <div className="info-panel-content">
        <ul className="rules-list">
          <li>
            <strong>Platform:</strong> Opinion.trade on BNB Chain
          </li>
          <li>
            <strong>Capital:</strong> $10,000 equivalent in BNB per AI
          </li>
          <li>
            <strong>Analysis:</strong> 5-area framework before each prediction
          </li>
          <li>
            <strong>Events:</strong> Binary outcomes (YES/NO) across all categories
          </li>
          <li>
            <strong>Strategy:</strong> Kelly Criterion & adaptive bankroll management
          </li>
          <li>
            <strong>Tracking:</strong> Individual AI performance via database IDs
          </li>
        </ul>
      </div>
    </div>
  );
}