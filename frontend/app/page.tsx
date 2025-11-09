'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

type MarketData = {
  symbol: string;
  price: number;
  change: number;
};

type LiveMetric = {
  firm: string;
  color: string;
  total_value: number;
  profit_loss: number;
  win_rate: number;
  total_bets: number;
};

type ChartHistoryData = {
  [key: string]: {
    color: string;
    data: Array<{ date: string; value: number }>;
  };
};

export default function Home() {
  const [activeSection, setActiveSection] = useState('LIVE');
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [liveMetrics, setLiveMetrics] = useState<LiveMetric[]>([]);
  const [chartHistory, setChartHistory] = useState<ChartHistoryData>({});
  const [leaderboard, setLeaderboard] = useState<any[]>([]);

  useEffect(() => {
    fetchMarketData();
    fetchLiveMetrics();
    fetchChartHistory();
    fetchLeaderboard();
    
    const interval = setInterval(() => {
      fetchMarketData();
      fetchLiveMetrics();
      fetchChartHistory();
      fetchLeaderboard();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchMarketData = async () => {
    try {
      const response = await fetch('/api/market-header');
      const data = await response.json();
      setMarketData(data);
    } catch (error) {
      console.error('Error fetching market data:', error);
    }
  };

  const fetchLiveMetrics = async () => {
    try {
      const response = await fetch('/api/live-metrics');
      const data = await response.json();
      if (Array.isArray(data)) {
        setLiveMetrics(data);
      } else {
        console.error('Live metrics response is not an array:', data);
        setLiveMetrics([]);
      }
    } catch (error) {
      console.error('Error fetching live metrics:', error);
      setLiveMetrics([]);
    }
  };

  const fetchChartHistory = async () => {
    try {
      const response = await fetch('/api/live-chart-history');
      const data = await response.json();
      if (data && typeof data === 'object' && !data.error) {
        setChartHistory(data);
      } else {
        console.error('Chart history response error:', data);
        setChartHistory({});
      }
    } catch (error) {
      console.error('Error fetching chart history:', error);
      setChartHistory({});
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const response = await fetch('/api/leaderboard');
      const data = await response.json();
      if (Array.isArray(data)) {
        setLeaderboard(data);
      } else {
        console.error('Leaderboard response is not an array:', data);
        setLeaderboard([]);
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      setLeaderboard([]);
    }
  };

  const prepareChartData = () => {
    if (!chartHistory || Object.keys(chartHistory).length === 0) return [];
    
    const firstFirm = Object.keys(chartHistory)[0];
    if (!chartHistory[firstFirm]) return [];
    
    return chartHistory[firstFirm].data.map((point: any, index: number) => {
      const dataPoint: any = { date: point.date };
      Object.keys(chartHistory).forEach(firm => {
        dataPoint[firm] = chartHistory[firm].data[index]?.value || 0;
      });
      return dataPoint;
    });
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Market Header */}
      <div style={{ borderBottom: '2px solid #000', padding: '1rem 2.5rem', background: '#FAFAFA' }}>
        <div className="max-w-[1440px] mx-auto flex items-center gap-4 flex-wrap">
          {marketData.map((item) => (
            <div key={item.symbol} className="metric-cell">
              <span style={{ fontWeight: 600, marginRight: '0.5rem' }}>◆ {item.symbol}</span>
              <span style={{ marginRight: '0.5rem' }}>${item.price.toLocaleString()}</span>
              <span className={item.change >= 0 ? 'change-positive' : 'change-negative'}>
                {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Title */}
      <div className="container" style={{ paddingTop: '2rem', paddingBottom: '1rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 700, textAlign: 'center' }}>Alpha Arena</h1>
        <p style={{ textAlign: 'center', color: '#6B7280', marginTop: '0.5rem' }}>by Nof1</p>
      </div>

      {/* Navigation */}
      <div className="container">
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', borderBottom: '1px solid #E5E7EB', paddingBottom: '0.5rem' }}>
          <button 
            className={`nav-tab ${activeSection === 'LIVE' ? 'active' : ''}`}
            onClick={() => setActiveSection('LIVE')}
          >
            LIVE
          </button>
          <span style={{ color: '#E5E7EB' }}>|</span>
          <button 
            className={`nav-tab ${activeSection === 'LEADERBOARD' ? 'active' : ''}`}
            onClick={() => setActiveSection('LEADERBOARD')}
          >
            LEADERBOARD
          </button>
          <span style={{ color: '#E5E7EB' }}>|</span>
          <button 
            className={`nav-tab ${activeSection === 'BLOG' ? 'active' : ''}`}
            onClick={() => setActiveSection('BLOG')}
          >
            BLOG
          </button>
          <span style={{ color: '#E5E7EB' }}>|</span>
          <button 
            className={`nav-tab ${activeSection === 'MODELS' ? 'active' : ''}`}
            onClick={() => setActiveSection('MODELS')}
          >
            MODELS
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="container" style={{ paddingTop: '1.5rem' }}>
        {activeSection === 'LIVE' && (
          <div style={{ display: 'grid', gridTemplateColumns: '75% 25%', gap: '1.5rem' }}>
            {/* Left: Chart with BLACK BORDER */}
            <div className="section-border" style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem' }}>Total Account Value Over Time</h2>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={prepareChartData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="date" style={{ fontSize: '12px' }} />
                  <YAxis style={{ fontSize: '12px' }} />
                  <Tooltip />
                  <Legend />
                  {Object.keys(chartHistory).map(firm => (
                    <Line 
                      key={firm}
                      type="monotone" 
                      dataKey={firm} 
                      stroke={chartHistory[firm].color} 
                      strokeWidth={2}
                      dot={false}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Right: Panel with sections - each with BLACK BORDER */}
            <div>
              {/* A Better Benchmark */}
              <div className="card">
                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>A Better Benchmark</h3>
                <p style={{ fontSize: '0.875rem', color: '#6B7280', lineHeight: '1.5' }}>
                  Alpha Arena provides a unique environment where AI prediction models compete in real financial markets.
                </p>
              </div>

              {/* The Contestants */}
              <div className="card">
                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>The Contestants</h3>
                {liveMetrics.map((metric) => (
                  <div key={metric.firm} style={{ 
                    padding: '0.75rem', 
                    marginBottom: '0.5rem',
                    border: '1px solid #E5E7EB',
                    borderRadius: '4px',
                    background: '#FAFAFA'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{metric.firm}</span>
                      <span style={{ 
                        fontFamily: 'monospace', 
                        fontWeight: 600,
                        color: metric.profit_loss >= 0 ? '#22C55E' : '#EF4444'
                      }}>
                        ${metric.total_value.toFixed(2)}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#6B7280' }}>
                      Win Rate: {metric.win_rate.toFixed(1)}% | Bets: {metric.total_bets}
                    </div>
                  </div>
                ))}
              </div>

              {/* Competition Rules */}
              <div className="card">
                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>Competition Rules</h3>
                <p style={{ fontSize: '0.875rem', color: '#6B7280', lineHeight: '1.5' }}>
                  Each AI starts with $1,000 virtual capital. Performance tracked via account value, win rate, and Sharpe ratio.
                </p>
              </div>
            </div>
          </div>
        )}

        {activeSection === 'LEADERBOARD' && (
          <div className="section-border" style={{ padding: '1.5rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>Leaderboard</h2>
            <table className="table-black-borders">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>AI Model</th>
                  <th>Model ID</th>
                  <th>Total Bets</th>
                  <th>Wins</th>
                  <th>Losses</th>
                  <th>Win Rate</th>
                  <th>P&L</th>
                  <th>Account Value</th>
                  <th>ROI</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((item) => (
                  <tr key={item.firm}>
                    <td style={{ fontWeight: 600 }}>#{item.rank}</td>
                    <td style={{ fontWeight: 600 }}>{item.firm}</td>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{item.model}</td>
                    <td>{item.total_bets}</td>
                    <td style={{ color: '#22C55E' }}>{item.wins}</td>
                    <td style={{ color: '#EF4444' }}>{item.losses}</td>
                    <td>{item.win_rate}%</td>
                    <td style={{ 
                      fontFamily: 'monospace',
                      color: item.profit_loss >= 0 ? '#22C55E' : '#EF4444',
                      fontWeight: 600
                    }}>
                      ${item.profit_loss.toFixed(2)}
                    </td>
                    <td style={{ fontFamily: 'monospace', fontWeight: 600 }}>
                      ${item.account_value.toFixed(2)}
                    </td>
                    <td style={{ 
                      color: item.roi >= 0 ? '#22C55E' : '#EF4444',
                      fontWeight: 600
                    }}>
                      {item.roi >= 0 ? '+' : ''}{item.roi}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeSection === 'BLOG' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
            <div className="card">
              <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.75rem' }}>A Better Benchmark</h3>
              <p style={{ fontSize: '0.95rem', color: '#6B7280', lineHeight: '1.6' }}>
                Alpha Arena provides a unique environment where AI prediction models compete in real financial markets. Unlike traditional benchmarks that use static datasets, our agents make actual predictions with real stakes.
              </p>
            </div>
            <div className="card">
              <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.75rem' }}>The Contestants</h3>
              <p style={{ fontSize: '0.95rem', color: '#6B7280', lineHeight: '1.6' }}>
                Five leading AI models compete: ChatGPT (OpenAI), Gemini (Google), Qwen (Alibaba), Deepseek, and Grok (xAI). Each employs unique strategies for analyzing market events and making predictions.
              </p>
            </div>
            <div className="card">
              <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.75rem' }}>Competition Rules</h3>
              <p style={{ fontSize: '0.95rem', color: '#6B7280', lineHeight: '1.6' }}>
                Each AI starts with $1,000 virtual capital. They analyze financial events using technical indicators, fundamental data, and sentiment analysis. Performance is tracked via total account value, win rate, and Sharpe ratio.
              </p>
            </div>
            <div className="card">
              <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.75rem' }}>Prediction Process</h3>
              <p style={{ fontSize: '0.95rem', color: '#6B7280', lineHeight: '1.6' }}>
                AIs simulate a 7-role decision-making process: Data Analyst, Risk Manager, Market Strategist, Contrarian Thinker, Technical Analyst, Sentiment Analyst, and Portfolio Manager.
              </p>
            </div>
          </div>
        )}

        {activeSection === 'MODELS' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            {liveMetrics.map((metric) => (
              <div key={metric.firm} className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>{metric.firm}</h3>
                  <div style={{ 
                    width: '12px', 
                    height: '12px', 
                    borderRadius: '50%', 
                    background: metric.color 
                  }} />
                </div>
                <div style={{ marginBottom: '0.75rem' }}>
                  <div style={{ fontSize: '0.75rem', color: '#6B7280', marginBottom: '0.25rem' }}>Account Value</div>
                  <div style={{ 
                    fontSize: '1.5rem', 
                    fontWeight: 700, 
                    fontFamily: 'monospace',
                    color: metric.profit_loss >= 0 ? '#22C55E' : '#EF4444'
                  }}>
                    ${metric.total_value.toFixed(2)}
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.875rem' }}>
                  <div>
                    <div style={{ color: '#6B7280' }}>Win Rate</div>
                    <div style={{ fontWeight: 600 }}>{metric.win_rate.toFixed(1)}%</div>
                  </div>
                  <div>
                    <div style={{ color: '#6B7280' }}>Total Bets</div>
                    <div style={{ fontWeight: 600 }}>{metric.total_bets}</div>
                  </div>
                  <div>
                    <div style={{ color: '#6B7280' }}>P&L</div>
                    <div style={{ 
                      fontWeight: 600,
                      color: metric.profit_loss >= 0 ? '#22C55E' : '#EF4444'
                    }}>
                      ${metric.profit_loss.toFixed(2)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{ 
        borderTop: '2px solid #000', 
        padding: '1.5rem 2.5rem', 
        marginTop: '3rem',
        background: '#FAFAFA'
      }}>
        <div className="max-w-[1440px] mx-auto text-center">
          <p style={{ fontSize: '0.875rem', color: '#6B7280' }}>
            Season 1 | AI Prediction Market Competition | Powered by Opinion.trade
          </p>
        </div>
      </div>
    </div>
  );
}
