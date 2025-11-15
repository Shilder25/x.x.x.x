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
  const [aiTrades, setAiTrades] = useState<{[key: string]: any[]}>({});
  const [cancelledOrders, setCancelledOrders] = useState<any[]>([]);

  useEffect(() => {
    fetchMarketData();
    fetchLiveMetrics();
    fetchChartHistory();
    fetchLeaderboard();
    fetchAIDecisions();
    fetchActivePositions();
    fetchCancelledOrders();
    
    const interval = setInterval(() => {
      fetchMarketData();
      fetchLiveMetrics();
      fetchChartHistory();
      fetchLeaderboard();
      fetchAIDecisions();
      fetchActivePositions();
      fetchCancelledOrders();
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

  const fetchAITrades = async (firmName: string) => {
    if (aiTrades[firmName]) return;
    
    try {
      const response = await fetch(getApiUrl(`/api/ai-trades/${firmName}?limit=50`));
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setAiTrades(prev => ({
            ...prev,
            [firmName]: data.trades || []
          }));
        }
      }
    } catch (error) {
      console.error(`Error fetching trades for ${firmName}:`, error);
    }
  };

  const fetchCancelledOrders = async () => {
    try {
      const response = await fetch(getApiUrl('/api/cancelled-orders?limit=50'));
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setCancelledOrders(data.cancelled_orders || []);
        }
      }
    } catch (error) {
      console.error('Error fetching cancelled orders:', error);
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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', padding: '0 2rem' }}>
            <div style={{ 
              marginBottom: '1rem',
              padding: '1.5rem',
              background: '#000',
              color: '#fff',
              border: '2px solid #000'
            }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>AI Trading Leaderboard</h2>
              <p style={{ fontSize: '0.875rem', color: '#9CA3AF' }}>Click on any AI to view their complete trade history</p>
            </div>
            
            {leaderboard.map((item, index) => {
              const firmColor = item.firm === 'ChatGPT' ? '#3B82F6' : 
                               item.firm === 'Gemini' ? '#8B5CF6' : 
                               item.firm === 'Qwen' ? '#F97316' : 
                               item.firm === 'Deepseek' ? '#FFF' : '#06B6D4';
              
              return (
                <details 
                  key={item.firm}
                  style={{ border: '2px solid #000', background: '#fff' }}
                  onToggle={(e) => {
                    if ((e.target as HTMLDetailsElement).open) {
                      fetchAITrades(item.firm);
                    }
                  }}
                >
                  <summary style={{ 
                    padding: '1.5rem', 
                    cursor: 'pointer',
                    display: 'grid',
                    gridTemplateColumns: '60px 1fr 150px 150px 120px 120px 120px',
                    gap: '1rem',
                    alignItems: 'center',
                    fontWeight: 500,
                    background: '#F9FAFB',
                    borderBottom: '2px solid #000'
                  }}>
                    <span style={{ fontSize: '1.25rem', fontWeight: 600, color: '#000' }}>#{index + 1}</span>
                    <span style={{ fontWeight: 600, color: firmColor }}>{item.firm}</span>
                    <span style={{ textAlign: 'right', color: '#374151' }}>${item.total_value?.toLocaleString() || '0'}</span>
                    <span style={{ 
                      textAlign: 'right',
                      color: item.profit_loss >= 0 ? '#10B981' : '#EF4444',
                      fontWeight: 600
                    }}>
                      {item.profit_loss >= 0 ? '+' : ''}${item.profit_loss?.toLocaleString() || '0'}
                    </span>
                    <span style={{ textAlign: 'right', color: '#374151' }}>{item.win_rate?.toFixed(1) || '0'}%</span>
                    <span style={{ textAlign: 'right', color: '#374151' }}>{item.total_bets || 0} bets</span>
                    <span style={{ textAlign: 'right', color: '#374151' }}>{item.accuracy?.toFixed(1) || '0'}%</span>
                  </summary>
                  
                  <div style={{ padding: '2rem', borderTop: '2px solid #000', background: '#fff' }}>
                    <h3 style={{ 
                      fontSize: '1.125rem', 
                      fontWeight: 600, 
                      marginBottom: '1.5rem',
                      padding: '0.75rem',
                      background: '#000',
                      color: '#fff',
                      border: '2px solid #000'
                    }}>
                      Trade History - {item.firm}
                    </h3>
                    
                    {!aiTrades[item.firm] ? (
                      <div style={{ padding: '2rem', textAlign: 'center', color: '#6B7280' }}>
                        Loading trades...
                      </div>
                    ) : aiTrades[item.firm].length === 0 ? (
                      <div style={{ padding: '2rem', textAlign: 'center', color: '#6B7280' }}>
                        No trades recorded yet
                      </div>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        {aiTrades[item.firm].slice(0, 20).map((trade, idx) => (
                          <div key={idx} style={{ 
                            padding: '1rem', 
                            border: '2px solid #000', 
                            background: '#fff'
                          }}>
                            <div style={{ 
                              display: 'flex', 
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              marginBottom: '0.75rem'
                            }}>
                              <div>
                                <div style={{ fontSize: '0.875rem', fontWeight: 600 }}>
                                  {trade.event_description}
                                </div>
                                <div style={{ fontSize: '0.75rem', color: '#6B7280', marginTop: '0.25rem' }}>
                                  {trade.category || 'General'} • {new Date(trade.execution_timestamp).toLocaleString()}
                                </div>
                              </div>
                              <div style={{ textAlign: 'right' }}>
                                <div style={{ 
                                  fontSize: '0.875rem', 
                                  fontWeight: 600,
                                  color: trade.actual_result === null ? '#6B7280' : 
                                         trade.actual_result === 1 ? '#10B981' : '#EF4444'
                                }}>
                                  {trade.actual_result === null ? 'PENDING' : 
                                   trade.actual_result === 1 ? 'WIN ✓' : 'LOSS ✗'}
                                </div>
                              </div>
                            </div>
                            
                            <div style={{ 
                              display: 'grid', 
                              gridTemplateColumns: 'repeat(4, 1fr)', 
                              gap: '1rem',
                              fontSize: '0.75rem'
                            }}>
                              <div>
                                <div style={{ color: '#6B7280', marginBottom: '0.25rem' }}>Bet Size</div>
                                <div style={{ fontWeight: 600 }}>${trade.bet_size?.toFixed(2) || '0'}</div>
                              </div>
                              <div>
                                <div style={{ color: '#6B7280', marginBottom: '0.25rem' }}>Probability</div>
                                <div style={{ fontWeight: 600 }}>{(trade.probability * 100).toFixed(0)}%</div>
                              </div>
                              <div>
                                <div style={{ color: '#6B7280', marginBottom: '0.25rem' }}>Confidence</div>
                                <div style={{ fontWeight: 600 }}>{trade.confidence || 'N/A'}/10</div>
                              </div>
                              <div>
                                <div style={{ color: '#6B7280', marginBottom: '0.25rem' }}>P/L</div>
                                <div style={{ 
                                  fontWeight: 600,
                                  color: trade.profit_loss > 0 ? '#10B981' : 
                                         trade.profit_loss < 0 ? '#EF4444' : '#6B7280'
                                }}>
                                  {trade.profit_loss !== null && trade.profit_loss !== undefined ? 
                                   `${trade.profit_loss >= 0 ? '+' : ''}$${trade.profit_loss.toFixed(2)}` : 
                                   '-'}
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </details>
              );
            })}
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
                className={`blog-tab ${activeBlogTab === 'CANCELLED ORDERS' ? 'active' : ''}`}
                onClick={() => setActiveBlogTab('CANCELLED ORDERS')}
              >
                CANCELLED ORDERS
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
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {aiDecisions.slice(0, 20).map((decision, idx) => (
                      <details key={idx} style={{ border: '2px solid #000', background: '#fff' }}>
                        <summary style={{ 
                          padding: '1rem', 
                          cursor: 'pointer', 
                          fontWeight: 600,
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}>
                          <span style={{ color: decision.firm_name === 'ChatGPT' ? '#3B82F6' : decision.firm_name === 'Gemini' ? '#8B5CF6' : decision.firm_name === 'Qwen' ? '#F97316' : decision.firm_name === 'Deepseek' ? '#000' : '#06B6D4' }}>
                            {decision.firm_name}
                          </span>
                          <span style={{ fontWeight: 400, flex: 1, marginLeft: '1rem', marginRight: '1rem' }}>
                            {decision.event_description}
                          </span>
                          <span style={{ fontSize: '0.875rem', color: '#6B7280' }}>
                            {(decision.probability * 100).toFixed(0)}% • ${decision.bet_size}
                          </span>
                        </summary>
                        <div style={{ padding: '1.5rem', borderTop: '2px solid #000', background: '#F9FAFB' }}>
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
                            <div>
                              <div style={{ fontSize: '0.75rem', color: '#6B7280', marginBottom: '0.25rem' }}>CATEGORY</div>
                              <div style={{ fontWeight: 600 }}>{decision.category || 'N/A'}</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.75rem', color: '#6B7280', marginBottom: '0.25rem' }}>CONFIDENCE</div>
                              <div style={{ fontWeight: 600 }}>{decision.confidence}/10</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.75rem', color: '#6B7280', marginBottom: '0.25rem' }}>RESULT</div>
                              <div style={{ fontWeight: 600, color: decision.actual_result === null ? '#6B7280' : decision.actual_result === 1 ? '#10B981' : '#EF4444' }}>
                                {decision.actual_result === null ? 'Pending' : decision.actual_result === 1 ? 'Win ✓' : 'Loss ✗'}
                              </div>
                            </div>
                          </div>

                          <div style={{ marginBottom: '1.5rem' }}>
                            <h4 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.75rem' }}>5-AREA ANALYSIS BREAKDOWN</h4>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.75rem' }}>
                              {['sentiment', 'news', 'technical', 'fundamental', 'volatility'].map(area => (
                                <div key={area} style={{ padding: '0.75rem', border: '1px solid #E5E7EB', background: '#fff' }}>
                                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#6B7280', marginBottom: '0.25rem' }}>
                                    {area}
                                  </div>
                                  <div style={{ fontSize: '1.25rem', fontWeight: 600, color: decision[`${area}_score`] >= 7 ? '#10B981' : decision[`${area}_score`] >= 5 ? '#F59E0B' : '#EF4444' }}>
                                    {decision[`${area}_score`] || 'N/A'}/10
                                  </div>
                                  <div style={{ fontSize: '0.7rem', color: '#6B7280', marginTop: '0.5rem', lineHeight: '1.3' }}>
                                    {decision[`${area}_analysis`] || 'No analysis available'}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>

                          {decision.probability_reasoning && (
                            <div style={{ padding: '1rem', background: '#FEF3C7', border: '1px solid #F59E0B' }}>
                              <div style={{ fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.5rem', color: '#92400E' }}>
                                💡 PROBABILITY CALCULATION REASONING
                              </div>
                              <div style={{ fontSize: '0.875rem', color: '#78350F', lineHeight: '1.5' }}>
                                {decision.probability_reasoning}
                              </div>
                            </div>
                          )}

                          <div style={{ fontSize: '0.75rem', color: '#6B7280', marginTop: '1rem' }}>
                            Timestamp: {new Date(decision.execution_timestamp).toLocaleString()}
                          </div>
                        </div>
                      </details>
                    ))}
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
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {activePositions.map((position, idx) => {
                      const potentialWin = position.bet_size * 2;
                      const potentialLoss = position.bet_size;
                      const expectedPL = (position.probability * potentialWin) - ((1 - position.probability) * potentialLoss);
                      
                      return (
                        <div key={idx} style={{ border: '2px solid #000', background: '#fff', padding: '1.5rem' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                            <div>
                              <div style={{ fontSize: '0.75rem', color: '#6B7280', marginBottom: '0.25rem' }}>
                                {position.category || 'GENERAL'} • {position.firm_name}
                              </div>
                              <div style={{ fontSize: '1rem', fontWeight: 600 }}>
                                {position.event_description}
                              </div>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                              <div style={{ fontSize: '0.75rem', color: '#6B7280', marginBottom: '0.25rem' }}>ACTIVE</div>
                              <div style={{ fontSize: '1.25rem', fontWeight: 600, color: '#10B981' }}>
                                {(position.probability * 100).toFixed(0)}%
                              </div>
                            </div>
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', padding: '1rem', background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
                            <div>
                              <div style={{ fontSize: '0.7rem', color: '#6B7280', marginBottom: '0.25rem' }}>BET SIZE</div>
                              <div style={{ fontSize: '1rem', fontWeight: 600 }}>${position.bet_size.toFixed(2)}</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.7rem', color: '#6B7280', marginBottom: '0.25rem' }}>POTENTIAL WIN</div>
                              <div style={{ fontSize: '1rem', fontWeight: 600, color: '#10B981' }}>+${potentialWin.toFixed(2)}</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.7rem', color: '#6B7280', marginBottom: '0.25rem' }}>POTENTIAL LOSS</div>
                              <div style={{ fontSize: '1rem', fontWeight: 600, color: '#EF4444' }}>-${potentialLoss.toFixed(2)}</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.7rem', color: '#6B7280', marginBottom: '0.25rem' }}>EXPECTED VALUE</div>
                              <div style={{ fontSize: '1rem', fontWeight: 600, color: expectedPL >= 0 ? '#10B981' : '#EF4444' }}>
                                {expectedPL >= 0 ? '+' : ''}${expectedPL.toFixed(2)}
                              </div>
                            </div>
                          </div>

                          {position.market_volume !== null && position.market_volume !== undefined && (
                            <div style={{ marginTop: '1rem', fontSize: '0.75rem', color: '#6B7280' }}>
                              Opinion.trade Market Volume: ${position.market_volume.toLocaleString()}
                            </div>
                          )}

                          <div style={{ fontSize: '0.75rem', color: '#6B7280', marginTop: '1rem' }}>
                            Opened: {new Date(position.execution_timestamp).toLocaleString()}
                          </div>
                        </div>
                      );
                    })}
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

            {activeBlogTab === 'CANCELLED ORDERS' && (
              <div className="blog-section">
                <div style={{ 
                  padding: '1.5rem',
                  background: '#000',
                  color: '#fff',
                  border: '2px solid #000',
                  marginBottom: '1.5rem'
                }}>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Cancelled Orders - 3-Strike System</h2>
                  <p style={{ fontSize: '0.875rem', color: '#9CA3AF' }}>
                    Orders automatically cancelled after 3 consecutive negative reviews (30-min monitoring intervals)
                  </p>
                </div>
                
                {cancelledOrders.length === 0 ? (
                  <div style={{ padding: '2rem', textAlign: 'center', color: '#6B7280', background: '#fff', border: '2px solid #000' }}>
                    No orders have been cancelled yet. The OrderMonitor system reviews active orders every 30 minutes.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {cancelledOrders.map((order, idx) => {
                      const firmColor = order.firm_name === 'ChatGPT' ? '#3B82F6' : 
                                       order.firm_name === 'Gemini' ? '#8B5CF6' : 
                                       order.firm_name === 'Qwen' ? '#F97316' : 
                                       order.firm_name === 'Deepseek' ? '#000' : '#06B6D4';
                      
                      let strikesHistory = [];
                      try {
                        strikesHistory = typeof order.strikes_history === 'string' 
                          ? JSON.parse(order.strikes_history) 
                          : order.strikes_history || [];
                      } catch (e) {
                        strikesHistory = [];
                      }
                      
                      return (
                        <details key={idx} style={{ border: '2px solid #000', background: '#fff' }}>
                          <summary style={{ 
                            padding: '1.25rem', 
                            cursor: 'pointer',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            fontWeight: 600,
                            background: '#000',
                            color: '#fff'
                          }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                              <span style={{ 
                                fontSize: '0.75rem', 
                                padding: '0.25rem 0.5rem', 
                                background: '#EF4444', 
                                color: '#fff',
                                borderRadius: '4px',
                                fontWeight: 600
                              }}>
                                CANCELLED
                              </span>
                              <span style={{ color: firmColor, fontSize: '1rem', fontWeight: 600 }}>
                                {order.firm_name}
                              </span>
                              <span style={{ fontSize: '0.875rem', color: '#9CA3AF' }}>
                                Order #{order.order_id}
                              </span>
                            </div>
                            <span style={{ fontSize: '0.75rem', color: '#9CA3AF' }}>
                              {new Date(order.timestamp).toLocaleString()}
                            </span>
                          </summary>
                          
                          <div style={{ padding: '1.5rem', borderTop: '2px solid #000', background: '#fff' }}>
                            <div style={{ marginBottom: '1.5rem', padding: '1rem', background: '#FEE2E2', border: '2px solid #EF4444' }}>
                              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#991B1B', marginBottom: '0.5rem' }}>
                                CANCELLATION REASON
                              </div>
                              <div style={{ fontSize: '0.875rem', color: '#7F1D1D' }}>
                                {order.cancel_reason}
                              </div>
                            </div>
                            
                            <h4 style={{ 
                              fontSize: '0.875rem', 
                              fontWeight: 600, 
                              marginBottom: '1rem',
                              padding: '0.75rem',
                              background: '#000',
                              color: '#fff',
                              border: '2px solid #000'
                            }}>
                              Strikes History ({strikesHistory.length} reviews)
                            </h4>
                            
                            {strikesHistory.length === 0 ? (
                              <div style={{ padding: '1rem', textAlign: 'center', color: '#6B7280', background: '#fff', border: '2px solid #000' }}>
                                No strike history recorded
                              </div>
                            ) : (
                              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                {strikesHistory.map((strike: any, sIdx: number) => (
                                  <div key={sIdx} style={{ 
                                    padding: '1rem', 
                                    border: `2px solid ${strike.strike_issued ? '#EF4444' : '#10B981'}`,
                                    background: strike.strike_issued ? '#FEF2F2' : '#F0FDF4',
                                    borderRadius: '4px'
                                  }}>
                                    <div style={{ 
                                      display: 'flex', 
                                      justifyContent: 'space-between',
                                      marginBottom: '0.75rem'
                                    }}>
                                      <span style={{ 
                                        fontSize: '0.75rem', 
                                        fontWeight: 600,
                                        color: strike.strike_issued ? '#991B1B' : '#166534'
                                      }}>
                                        Review #{sIdx + 1}
                                      </span>
                                      <span style={{ 
                                        fontSize: '0.75rem', 
                                        padding: '0.25rem 0.5rem',
                                        background: strike.strike_issued ? '#EF4444' : '#10B981',
                                        color: '#fff',
                                        borderRadius: '4px',
                                        fontWeight: 600
                                      }}>
                                        {strike.strike_issued ? '⚠ STRIKE' : '✓ PASS'}
                                      </span>
                                    </div>
                                    
                                    <div style={{ 
                                      display: 'grid', 
                                      gridTemplateColumns: 'repeat(3, 1fr)',
                                      gap: '0.75rem',
                                      fontSize: '0.75rem',
                                      marginBottom: '0.75rem'
                                    }}>
                                      <div>
                                        <div style={{ color: '#6B7280', marginBottom: '0.25rem' }}>Price Manipulation</div>
                                        <div style={{ 
                                          fontWeight: 600,
                                          color: strike.factors?.price_manipulation ? '#EF4444' : '#10B981'
                                        }}>
                                          {strike.factors?.price_manipulation ? 'YES ✗' : 'NO ✓'}
                                        </div>
                                      </div>
                                      <div>
                                        <div style={{ color: '#6B7280', marginBottom: '0.25rem' }}>Stagnation {'>'}1wk</div>
                                        <div style={{ 
                                          fontWeight: 600,
                                          color: strike.factors?.time_stagnation ? '#EF4444' : '#10B981'
                                        }}>
                                          {strike.factors?.time_stagnation ? 'YES ✗' : 'NO ✓'}
                                        </div>
                                      </div>
                                      <div>
                                        <div style={{ color: '#6B7280', marginBottom: '0.25rem' }}>AI Contradiction</div>
                                        <div style={{ 
                                          fontWeight: 600,
                                          color: strike.factors?.ai_contradiction ? '#EF4444' : '#10B981'
                                        }}>
                                          {strike.factors?.ai_contradiction ? 'YES ✗' : 'NO ✓'}
                                        </div>
                                      </div>
                                    </div>
                                    
                                    {strike.reason && (
                                      <div style={{ 
                                        fontSize: '0.75rem', 
                                        color: '#6B7280',
                                        padding: '0.75rem',
                                        background: '#F9FAFB',
                                        border: '2px solid #E5E7EB'
                                      }}>
                                        {strike.reason}
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </details>
                      );
                    })}
                  </div>
                )}
                
                <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#fff', border: '2px solid #000' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem', color: '#000' }}>
                    How the 3-Strike System Works
                  </h3>
                  <ul style={{ fontSize: '0.875rem', color: '#374151', lineHeight: '1.6', paddingLeft: '1.5rem' }}>
                    <li style={{ marginBottom: '0.5rem' }}>
                      OrderMonitor reviews all active positions every 30 minutes
                    </li>
                    <li style={{ marginBottom: '0.5rem' }}>
                      Each review checks 3 factors: Price manipulation ({'>'}15% change), Time stagnation ({'>'}1 week), AI contradiction
                    </li>
                    <li style={{ marginBottom: '0.5rem' }}>
                      Strike issued if ANY factor triggers; strike count RESETS to 0 when all factors clear
                    </li>
                    <li style={{ marginBottom: '0.5rem' }}>
                      After 3 CONSECUTIVE strikes, order is automatically cancelled via Opinion.trade API
                    </li>
                    <li>
                      All reviews logged with detailed factor breakdown and cancellation reasons
                    </li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}

        {activeSection === 'MODELS' && (
          <div style={{ padding: '2rem' }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem', textAlign: 'center', borderBottom: '2px solid #000', paddingBottom: '1rem' }}>
              AI Model Details & Performance
            </h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
              {[
                { name: 'ChatGPT', model: 'gpt-4', strategy: 'Kelly Conservative', color: '#3B82F6', description: 'Conservative risk management with proven Kelly Criterion formula' },
                { name: 'Gemini', model: 'gemini-2.0-flash-exp', strategy: 'Martingale Modified', color: '#8B5CF6', description: 'Increases bet size after losses with strict limits to recover quickly' },
                { name: 'Qwen', model: 'qwen-plus', strategy: 'Fixed Fractional', color: '#F97316', description: 'Fixed percentage betting based on confidence levels for consistency' },
                { name: 'Deepseek', model: 'deepseek-chat', strategy: 'Proportional', color: '#000000', description: 'Bet size proportional to combined probability and confidence scores' },
                { name: 'Grok', model: 'grok-beta', strategy: 'Anti-Martingale', color: '#06B6D4', description: 'Increases bet size after wins to capitalize on winning streaks' }
              ].map((ai) => {
                const aiMetrics = liveMetrics.find(m => m.firm === ai.name) || {
                  firm: ai.name,
                  total_value: 0,
                  profit_loss: 0,
                  win_rate: 0,
                  total_bets: 0
                };
                return (
                  <div key={ai.name} style={{ border: '2px solid #000', background: '#fff', padding: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: ai.color }}>
                        {ai.name}
                      </h3>
                      <div style={{ fontSize: '0.75rem', padding: '0.25rem 0.75rem', background: '#F3F4F6', border: '1px solid #E5E7EB', borderRadius: '4px' }}>
                        {ai.strategy}
                      </div>
                    </div>

                    <div style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid #E5E7EB' }}>
                      <div style={{ fontSize: '0.75rem', color: '#6B7280', marginBottom: '0.25rem' }}>MODEL</div>
                      <div style={{ fontSize: '0.875rem', fontWeight: 500 }}>{ai.model}</div>
                    </div>

                    <div style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid #E5E7EB' }}>
                      <div style={{ fontSize: '0.75rem', color: '#6B7280', marginBottom: '0.5rem' }}>STRATEGY DESCRIPTION</div>
                      <div style={{ fontSize: '0.875rem', lineHeight: '1.5', color: '#374151' }}>{ai.description}</div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', marginBottom: '1rem' }}>
                      <div>
                        <div style={{ fontSize: '0.7rem', color: '#6B7280', marginBottom: '0.25rem' }}>TOTAL VALUE</div>
                        <div style={{ fontSize: '1.125rem', fontWeight: 600 }}>
                          ${aiMetrics.total_value?.toLocaleString() || '0'}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.7rem', color: '#6B7280', marginBottom: '0.25rem' }}>PROFIT/LOSS</div>
                        <div style={{ fontSize: '1.125rem', fontWeight: 600, color: (aiMetrics.profit_loss || 0) >= 0 ? '#10B981' : '#EF4444' }}>
                          {(aiMetrics.profit_loss || 0) >= 0 ? '+' : ''}${aiMetrics.profit_loss?.toLocaleString() || '0'}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.7rem', color: '#6B7280', marginBottom: '0.25rem' }}>WIN RATE</div>
                        <div style={{ fontSize: '1.125rem', fontWeight: 600 }}>
                          {aiMetrics.win_rate?.toFixed(1) || '0'}%
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.7rem', color: '#6B7280', marginBottom: '0.25rem' }}>TOTAL BETS</div>
                        <div style={{ fontSize: '1.125rem', fontWeight: 600 }}>
                          {aiMetrics.total_bets || 0}
                        </div>
                      </div>
                    </div>

                    <div style={{ padding: '0.75rem', background: '#F9FAFB', border: '1px solid #E5E7EB', fontSize: '0.75rem' }}>
                      <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>Risk Tier System</div>
                      <div style={{ color: '#6B7280' }}>
                        Adaptive 4-tier risk management: Conservative → Moderate → Aggressive → All-In, 
                        based on performance and drawdown levels
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#F9FAFB', border: '2px solid #000' }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>About the Betting Strategies</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', fontSize: '0.875rem' }}>
                <div>
                  <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>Kelly Conservative</div>
                  <div style={{ color: '#6B7280' }}>Uses 25% of Kelly fraction for safety, adjusts based on confidence</div>
                </div>
                <div>
                  <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>Martingale Modified</div>
                  <div style={{ color: '#6B7280' }}>1.5x multiplier after losses, max 3 consecutive increases</div>
                </div>
                <div>
                  <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>Fixed Fractional</div>
                  <div style={{ color: '#6B7280' }}>0.5-2% of bankroll based on confidence tiers</div>
                </div>
                <div>
                  <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>Proportional</div>
                  <div style={{ color: '#6B7280' }}>Bet size scales with probability × confidence score</div>
                </div>
                <div>
                  <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>Anti-Martingale</div>
                  <div style={{ color: '#6B7280' }}>1.3x multiplier after wins, max 3 consecutive increases</div>
                </div>
              </div>
            </div>
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