'use client';

import { useState, useEffect } from 'react';
import MarketHeader from '@/components/MarketHeader';
import NavigationTabs from '@/components/NavigationTabs';
import PerformanceChart from '@/components/PerformanceChart';
import { BenchmarkPanel, ContestantsPanel, CompetitionRulesPanel } from '@/components/InfoPanels';
import AIThinkingPanel from '@/components/AIThinkingPanel';
import { getApiUrl } from '@/lib/config';

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
  const [activeBlogTab, setActiveBlogTab] = useState('PREDICTION ANALYSIS');
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [liveMetrics, setLiveMetrics] = useState<LiveMetric[]>([]);
  const [chartHistory, setChartHistory] = useState<ChartHistoryData>({});
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [aiDecisions, setAiDecisions] = useState<any[]>([]);
  const [activePositions, setActivePositions] = useState<any[]>([]);

  useEffect(() => {
    fetchMarketData();
    fetchLiveMetrics();
    fetchChartHistory();
    fetchLeaderboard();
    fetchAIDecisions();
    fetchActivePositions();
    
    const interval = setInterval(() => {
      fetchMarketData();
      fetchLiveMetrics();
      fetchChartHistory();
      fetchLeaderboard();
      fetchAIDecisions();
      fetchActivePositions();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchMarketData = async () => {
    try {
      const response = await fetch(getApiUrl('/api/market-header'));
      const data = await response.json();
      setMarketData(data);
    } catch (error) {
      console.error('Error fetching market data:', error);
    }
  };

  const fetchLiveMetrics = async () => {
    try {
      const response = await fetch(getApiUrl('/api/live-metrics'));
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
      const response = await fetch(getApiUrl('/api/live-chart-history'));
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
      const response = await fetch(getApiUrl('/api/leaderboard'));
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

  const fetchAIDecisions = async () => {
    try {
      const response = await fetch(getApiUrl('/api/ai-decisions-history?limit=50'));
      if (response.ok) {
        const data = await response.json();
        setAiDecisions(data);
      }
    } catch (error) {
      console.error('Error fetching AI decisions:', error);
    }
  };

  const fetchActivePositions = async () => {
    try {
      const response = await fetch(getApiUrl('/api/active-positions'));
      if (response.ok) {
        const data = await response.json();
        setActivePositions(data);
      }
    } catch (error) {
      console.error('Error fetching active positions:', error);
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
          <div>
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
            
            {/* AI Thinking Panel - Below the chart */}
            <AIThinkingPanel />
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
              <button 
                className={`blog-tab ${activeBlogTab === 'PREDICTION ANALYSIS' ? 'active' : ''}`}
                onClick={() => setActiveBlogTab('PREDICTION ANALYSIS')}
              >
                PREDICTION ANALYSIS
              </button>
              <button 
                className={`blog-tab ${activeBlogTab === 'AI DECISIONS' ? 'active' : ''}`}
                onClick={() => setActiveBlogTab('AI DECISIONS')}
              >
                AI DECISIONS
              </button>
              <button 
                className={`blog-tab ${activeBlogTab === 'POSITIONS' ? 'active' : ''}`}
                onClick={() => setActiveBlogTab('POSITIONS')}
              >
                POSITIONS
              </button>
              <button 
                className={`blog-tab ${activeBlogTab === 'METHODOLOGY' ? 'active' : ''}`}
                onClick={() => setActiveBlogTab('METHODOLOGY')}
              >
                METHODOLOGY
              </button>
            </div>
            
            {activeBlogTab === 'PREDICTION ANALYSIS' && (
              <>
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
              </>
            )}

            {activeBlogTab === 'AI DECISIONS' && (
              <div className="blog-section">
                <h2>AI Decision History</h2>
                <p style={{ marginBottom: '1rem', color: '#6B7280' }}>
                  Complete history of AI predictions with transparent 5-area analysis breakdown
                </p>
                {aiDecisions.length === 0 ? (
                  <p style={{ padding: '2rem', textAlign: 'center', color: '#6B7280' }}>
                    No AI decisions recorded yet. System will log all predictions when enabled.
                  </p>
                ) : (
                  <div style={{ overflowX: 'auto' }}>
                    <table className="leaderboard-table">
                      <thead>
                        <tr>
                          <th>AI</th>
                          <th>EVENT</th>
                          <th>CATEGORY</th>
                          <th>PROB</th>
                          <th>CONFIDENCE</th>
                          <th>BET SIZE</th>
                          <th>RESULT</th>
                          <th>TIMESTAMP</th>
                        </tr>
                      </thead>
                      <tbody>
                        {aiDecisions.slice(0, 20).map((decision, idx) => (
                          <tr key={idx}>
                            <td style={{ fontWeight: 600 }}>{decision.firm_name}</td>
                            <td style={{ maxWidth: '200px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                              {decision.event_description}
                            </td>
                            <td>{decision.category || 'N/A'}</td>
                            <td>{(decision.probability * 100).toFixed(0)}%</td>
                            <td>{decision.confidence}/10</td>
                            <td>${decision.bet_size}</td>
                            <td>{decision.actual_result === null ? 'Pending' : decision.actual_result === 1 ? 'Win' : 'Loss'}</td>
                            <td style={{ fontSize: '0.75rem' }}>{new Date(decision.execution_timestamp).toLocaleDateString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {activeBlogTab === 'POSITIONS' && (
              <div className="blog-section">
                <h2>Active Positions</h2>
                <p style={{ marginBottom: '1rem', color: '#6B7280' }}>
                  Current unresolved predictions across all AIs on Opinion.trade
                </p>
                {activePositions.length === 0 ? (
                  <p style={{ padding: '2rem', textAlign: 'center', color: '#6B7280' }}>
                    No active positions. All predictions have been resolved.
                  </p>
                ) : (
                  <div style={{ overflowX: 'auto' }}>
                    <table className="leaderboard-table">
                      <thead>
                        <tr>
                          <th>AI</th>
                          <th>EVENT</th>
                          <th>CATEGORY</th>
                          <th>BET SIZE</th>
                          <th>PROB</th>
                          <th>EXPECTED VALUE</th>
                          <th>TIMESTAMP</th>
                        </tr>
                      </thead>
                      <tbody>
                        {activePositions.map((position, idx) => (
                          <tr key={idx}>
                            <td style={{ fontWeight: 600 }}>{position.firm_name}</td>
                            <td style={{ maxWidth: '250px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                              {position.event_description}
                            </td>
                            <td>{position.category || 'N/A'}</td>
                            <td>${position.bet_size}</td>
                            <td>{(position.probability * 100).toFixed(0)}%</td>
                            <td>{position.expected_value ? `$${position.expected_value.toFixed(2)}` : 'N/A'}</td>
                            <td style={{ fontSize: '0.75rem' }}>{new Date(position.execution_timestamp).toLocaleDateString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {activeBlogTab === 'METHODOLOGY' && (
              <div className="blog-section">
                <h2>5-Area Analysis Methodology</h2>
                <p>
                  Each AI performs a comprehensive analysis across 5 distinct areas before making any prediction:
                </p>
                
                <div style={{ marginTop: '1.5rem' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>1. Market Sentiment Analysis</h3>
                  <p style={{ fontSize: '0.875rem', color: '#6B7280', marginBottom: '1rem' }}>
                    Analyzes social media trends, Reddit discussions, community sentiment, and public opinion to gauge market psychology and crowd behavior.
                  </p>

                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>2. News Impact Analysis</h3>
                  <p style={{ fontSize: '0.875rem', color: '#6B7280', marginBottom: '1rem' }}>
                    Evaluates real-time news events, media coverage, event correlations, and breaking developments that could influence the outcome.
                  </p>

                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>3. Technical Indicators</h3>
                  <p style={{ fontSize: '0.875rem', color: '#6B7280', marginBottom: '1rem' }}>
                    Examines price patterns, volume analysis, market microstructure, and technical signals relevant to the prediction event.
                  </p>

                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>4. Fundamental Data</h3>
                  <p style={{ fontSize: '0.875rem', color: '#6B7280', marginBottom: '1rem' }}>
                    Reviews on-chain metrics, project fundamentals, economic indicators, and underlying value drivers specific to the event.
                  </p>

                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>5. Volatility & Risk Assessment</h3>
                  <p style={{ fontSize: '0.875rem', color: '#6B7280', marginBottom: '1rem' }}>
                    Measures market fluctuations, uncertainty levels, historical volatility patterns, and overall risk profile of the prediction.
                  </p>
                </div>

                <div style={{ marginTop: '2rem', padding: '1rem', background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
                  <p style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>Transparency Principle:</p>
                  <p style={{ fontSize: '0.875rem', color: '#6B7280' }}>
                    Every analysis score and reasoning text is stored in the database and exposed via API endpoints, 
                    allowing full transparency and validation of AI decision-making processes.
                  </p>
                </div>
              </div>
            )}
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