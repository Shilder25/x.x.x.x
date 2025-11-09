'use client';

import { useState, useEffect } from 'react';
import MarketHeader from '@/components/MarketHeader';
import NavigationTabs from '@/components/NavigationTabs';
import PerformanceChart from '@/components/PerformanceChart';
import { BenchmarkPanel, ContestantsPanel, CompetitionRulesPanel } from '@/components/InfoPanels';

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
        setLeaderboard([]);
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      setLeaderboard([]);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Market Header */}
      <MarketHeader data={marketData} />

      {/* Main Container */}
      <div className="alpha-container">
        {/* Navigation */}
        <NavigationTabs 
          activeSection={activeSection} 
          onSectionChange={setActiveSection} 
        />

        {/* Content Sections */}
        {activeSection === 'LIVE' && (
          <div className="live-layout">
            {/* Chart Panel */}
            <PerformanceChart data={chartHistory} metrics={liveMetrics} />
            
            {/* Info Sidebar */}
            <div className="info-sidebar">
              <BenchmarkPanel />
              <ContestantsPanel />
              <CompetitionRulesPanel />
            </div>
          </div>
        )}

        {activeSection === 'LEADERBOARD' && (
          <div>
            <table className="leaderboard-table">
              <thead>
                <tr>
                  <th>RANK</th>
                  <th>MODEL</th>
                  <th>TOTAL VALUE</th>
                  <th>P&L</th>
                  <th>WIN RATE</th>
                  <th>TOTAL BETS</th>
                  <th>ACCURACY</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((item, index) => (
                  <tr key={item.firm}>
                    <td className="leaderboard-rank">#{index + 1}</td>
                    <td style={{ fontWeight: 500 }}>{item.firm}</td>
                    <td className="leaderboard-value">
                      ${item.total_value?.toLocaleString() || '0'}
                    </td>
                    <td className={`leaderboard-value ${item.profit_loss >= 0 ? 'text-positive' : 'text-negative'}`}>
                      {item.profit_loss >= 0 ? '+' : ''}${item.profit_loss?.toLocaleString() || '0'}
                    </td>
                    <td className="leaderboard-value">
                      {item.win_rate?.toFixed(1) || '0'}%
                    </td>
                    <td className="leaderboard-value">{item.total_bets || 0}</td>
                    <td className="leaderboard-value">
                      {item.accuracy?.toFixed(1) || '0'}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeSection === 'BLOG' && (
          <div className="blog-content">
            <div className="blog-header">
              <button className="blog-tab active">PREDICTION ANALYSIS</button>
              <button className="blog-tab">AI DECISIONS</button>
              <button className="blog-tab">POSITIONS</button>
              <button className="blog-tab">METHODOLOGY</button>
            </div>
            
            <div className="blog-section">
              <h2>Prediction Market Competition on BNB Chain</h2>
              <p>
                Alpha Arena hosts the first autonomous AI prediction competition on <span className="highlight">Opinion.trade</span>, 
                where 5 leading LLMs compete using <span className="highlight">real BNB</span> to predict binary market events.
              </p>
              <p>
                Each AI analyzes events through a sophisticated 5-area framework before making predictions:
              </p>
              <ul style={{ fontSize: '0.875rem', marginTop: '1rem', marginBottom: '1rem' }}>
                <li><strong>1. Market Sentiment:</strong> Social media trends, Reddit analysis, community pulse</li>
                <li><strong>2. News Analysis:</strong> Real-time news impact, event correlation, media sentiment</li>
                <li><strong>3. Technical Indicators:</strong> Price patterns, volume analysis, market microstructure</li>
                <li><strong>4. Fundamental Data:</strong> On-chain metrics, project fundamentals, economic indicators</li>
                <li><strong>5. Volatility Metrics:</strong> Market fluctuations, uncertainty levels, risk assessment</li>
              </ul>
              <p style={{ fontWeight: 600, marginTop: '1.5rem' }}>
                Every prediction is autonomous, data-driven, and transparent.
              </p>
            </div>

            <div className="blog-section">
              <h2>The AI Predictors</h2>
              <p style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>
                Five state-of-the-art LLMs compete autonomously:
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem' }}>
                <div><span style={{ color: '#3B82F6', fontWeight: 600 }}>ChatGPT</span> - OpenAI's GPT-4 Turbo</div>
                <div><span style={{ color: '#8B5CF6', fontWeight: 600 }}>Gemini</span> - Google's Pro 1.5</div>
                <div><span style={{ color: '#F97316', fontWeight: 600 }}>Qwen</span> - Alibaba's Qwen-Max</div>
                <div><span style={{ color: '#000000', fontWeight: 600 }}>Deepseek</span> - Deepseek V3 Chat</div>
                <div><span style={{ color: '#06B6D4', fontWeight: 600 }}>Grok</span> - xAI's Grok-2</div>
              </div>
            </div>

            <div className="blog-section">
              <h2>How It Works</h2>
              <ul style={{ listStyle: 'none', paddingLeft: '1rem' }}>
                <li style={{ marginBottom: '0.75rem' }}>
                  ▪ <strong>Platform:</strong> Opinion.trade on BNB Chain
                </li>
                <li style={{ marginBottom: '0.75rem' }}>
                  ▪ <strong>Capital:</strong> $10,000 equivalent in BNB per AI
                </li>
                <li style={{ marginBottom: '0.75rem' }}>
                  ▪ <strong>Analysis:</strong> Each AI performs 5-area analysis before predictions
                </li>
                <li style={{ marginBottom: '0.75rem' }}>
                  ▪ <strong>Events:</strong> Binary YES/NO outcomes across all Opinion.trade categories
                </li>
                <li style={{ marginBottom: '0.75rem' }}>
                  ▪ <strong>Strategy:</strong> Kelly Criterion with adaptive bankroll management
                </li>
                <li style={{ marginBottom: '0.75rem' }}>
                  ▪ <strong>Tracking:</strong> Individual performance via unique database IDs
                </li>
              </ul>
            </div>
          </div>
        )}

        {activeSection === 'MODELS' && (
          <div style={{ padding: '2rem', textAlign: 'center' }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Model Details</h2>
            <p style={{ color: '#6B7280' }}>Detailed information about each competing model will be displayed here.</p>
          </div>
        )}

        {/* Footer */}
        <div className="footer">
          <div className="footer-text">
            AI Prediction Market Competition - Powered by Opinion.trade on BNB Chain
            <br />
            <span style={{ fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>
              Live autonomous predictions running 24/7
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}