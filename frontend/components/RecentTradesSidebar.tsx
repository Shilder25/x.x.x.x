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

export default function RecentTradesSidebar() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRecentTrades();
    
    const interval = setInterval(() => {
      fetchRecentTrades();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

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
      <h3 className="info-panel-title">Recent Trades</h3>
      <div className="info-panel-content" style={{ maxHeight: '500px', overflowY: 'auto' }}>
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
    </div>
  );
}
