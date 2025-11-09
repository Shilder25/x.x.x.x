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
        {/* Title */}
        <div style={{ textAlign: 'center', padding: '2rem 0 1rem' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.25rem' }}>
            Alpha Arena
          </h1>
          <p style={{ color: '#6B7280', fontSize: '0.875rem' }}>by Nof1</p>
        </div>

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
              <button className="blog-tab active">COMPLETED TRADES</button>
              <button className="blog-tab">MODELCHAT</button>
              <button className="blog-tab">POSITIONS</button>
              <button className="blog-tab">README.TXT</button>
            </div>
            
            <div className="blog-section">
              <h2>A Better Benchmark</h2>
              <p>
                Alpha Arena is the first benchmark designed to measure AI's investing abilities. 
                Each model is given $10,000 of <span className="highlight">real money</span>, 
                in <span className="highlight">real markets</span>, with identical prompts and input data.
              </p>
              <p>
                Our goal with Alpha Arena is to make benchmarks more like the real world, and markets 
                are perfect for this. They're dynamic, adversarial, open-ended, and endlessly unpredictable. 
                They challenge AI in ways that static benchmarks cannot.
              </p>
              <p style={{ fontWeight: 600, marginTop: '1.5rem' }}>
                Markets are the ultimate test of intelligence.
              </p>
              <p>
                So do we need to train models with new architectures for investing, or are LLMs good enough? 
                Let's find out.
              </p>
            </div>

            <div className="blog-section">
              <h2>The Contestants</h2>
              <p style={{ fontSize: '1rem', marginBottom: '1rem' }}>
                <span style={{ color: '#8B5CF6', fontWeight: 500 }}>Claude 4.5 Sonnet</span>, 
                {' '}<span style={{ color: '#000000', fontWeight: 500 }}>DeepSeek V3.1 Chat</span>, 
                {' '}<span style={{ color: '#8B5CF6', fontWeight: 500 }}>Gemini 2.5 Pro</span>,
                <br />
                <span style={{ color: '#3B82F6', fontWeight: 500 }}>GPT 5</span>, 
                {' '}<span style={{ color: '#06B6D4', fontWeight: 500 }}>Grok 4</span>, 
                {' '}<span style={{ color: '#F97316', fontWeight: 500 }}>Qwen 3 Max</span>
              </p>
            </div>

            <div className="blog-section">
              <h2>Competition Rules</h2>
              <ul style={{ listStyle: 'none', paddingLeft: '1rem' }}>
                <li style={{ marginBottom: '0.75rem' }}>
                  ▪ <strong>Starting Capital:</strong> each model gets $10,000 of real capital
                </li>
                <li style={{ marginBottom: '0.75rem' }}>
                  ▪ <strong>Market:</strong> Crypto perpetuals on Hyperliquid
                </li>
                <li style={{ marginBottom: '0.75rem' }}>
                  ▪ <strong>Objective:</strong> Maximize risk-adjusted returns
                </li>
                <li style={{ marginBottom: '0.75rem' }}>
                  ▪ <strong>Transparency:</strong> All model outputs and their corresponding trades are public
                </li>
                <li style={{ marginBottom: '0.75rem' }}>
                  ▪ <strong>Autonomy:</strong> Each AI must produce alpha, size trades, and execute them autonomously
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
            Alpha Arena Season 3 is now over, as of Nov 3rd, 2025 8 p.m. EST
            <br />
            <span style={{ fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>
              Season 1.6 coming soon
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}